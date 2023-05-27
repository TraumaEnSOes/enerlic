import asyncio
import logging


from .end_of_line import EndOfLine


class WireException( Exception ):
    pass


class Ping:
    @staticmethod
    def toWire( ) -> bytes:
        return b"I\n"


class Pong:
    @staticmethod
    def toWire( ) -> bytes:
        return b"O\n"


class Disconnected:
    pass


class Connection:
    def __init__( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter ):
        log = logging.getLogger( "connection" )

        self._stop = True
        self._log = log
        self._reader = reader
        self._writer = writer
        self._dataReceived = False

        self.clearListeners( )

    def run( self ):
        self._stop = False
        self._readTask = asyncio.create_task( self._readTaskBody( ) )

    def running( self ) -> bool:
        return self._stop == False

    def onException( self, target = None ):
        self._onException = target

    def onStop( self, target = None ):
        self._onStop = target

    def clearListeners( self ):
        self._onException = None
        self._onStop = None

    def dataReceived( self ):
        return self._dataReceived

    def clearDataReceived( self ):
        self._dataReceived = False

    async def ping( self ) -> None:
        if self.running( ):
            await self._writer.drain( )
            self._writer.write( Ping.toWire( ) )

    async def stop( self ):
        if ( self._stop == False ) and ( self._readTask is not None ):
            self._stop = True
            await self._cleanup( )
            self._readTask.cancel( )

    @staticmethod
    async def _callListener( target, *args, **kargs ):
        if target is not None:
            if asyncio.iscoroutinefunction( target ):
                await target( *args, **kargs )
            else:
                target( *args, **kargs )

    @staticmethod
    def _stripDataToSend( self, data: str | bytes ) -> bytes | None:
        if len( data ) == 0:
            return
            
        if isinstance( data, str ):
            data = data.encode( )

        data = data.strip( )

        if len( data ) == 0:
            return

        data = data + EndOfLine

        return data

    async def _cleanup( self ):
        await self._writer.drain( )
        self._writer.close( )
        await self._writer.wait_closed( )
        await Connection._callListener( self._onStop, self )

    async def _processMessage( self, msg ) -> None:
        log = self._log

        if isinstance( msg, Disconnected ):
            self._stop = True
        else:
            self._dataReceived = True

            if isinstance( msg, WireException ):
                self._stop = True
                await Connection._callListener( self._onException, self, msg )

            elif isinstance( msg, Ping ):
                await self._writer.drain( )
                self._writer.write( Pong.toWire( ) )

            elif isinstance( msg, Pong ):
                pass

            else:
                self._stop = True
                errorMsg = "Internal error in '_process': Unknown message type"
                log.error( errorMsg )
                await Connection._callListener( self._onException, self, Exception( errorMsg ) )

    def _parseMessagefromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException:
        log = self._log

        if len( line ) == 0:
            return Disconnected( )
        elif line == "I":
            return Ping( )
        elif line == "O":
            return Pong( )
        else:
            errorMsg = "Received invalid message"
            log.error( errorMsg )
            return WireException( errorMsg )

    async def _readTaskBody( self ) -> None:
        while self._stop == False:
            lineInBytes = await self._reader.readline( )
            stringLine = "" if len( lineInBytes ) == 0 else lineInBytes.decode( ).strip( )

            message = self._parseMessagefromWire( stringLine )

            await self._processMessage( message )

        await self._cleanup( )

