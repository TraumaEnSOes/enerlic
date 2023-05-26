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


class Disconnect:
    @staticmethod
    def toWire( ) -> bytes:
        return b"C\n"


class Connection:
    def __init__( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter ):
        log = logging.getLogger( "connection" )

        self._stop = False
        self._log = log
        self._reader = reader
        self._writer = writer
        self._dataReceived = False

        self.clearListeners( )

    def run( self ):
        self._readTask = asyncio.create_task( self._readTaskBody( ) )

    def onException( self, target = None ):
        self._onException = target

    def onDisconnected( self, target = None ):
        self._onDisconnected = target

    def onStop( self, target = None ):
        self._onStop = target

    def clearListeners( self ):
        self._onException = None
        self._onDisconnected = None
        self._onStop = None

    def dataReceived( self ):
        return self._dataReceived

    def clearDataReceived( self ):
        self._dataReceived = False

    async def notifyDisconnection( self ):
        await self._write( b"C" )

    async def stop( self ):
        if self._readTask is not None:
            self._stop = True
            await self._writer.drain( )
            self._writer.close( )
            await self._writer.wait_closed( )
            self._readTask.cancel( )

    @staticmethod
    async def _callListener( target, *args, **kargs ):
        if target is not None:
            if asyncio.iscoroutinefunction( target ):
                await target( *args, **kargs )
            else:
                target( *args, **kargs )

    @staticmethod
    def _stripFromWire( line: bytes ):
        if len( line ) == 0:
            raise WireException( "Received invalid, empty message" )

        if line[-1] != EndOfLine:
            raise WireException( "Received invalid message" )

        stringLine = line.decode( ).strip( )

        if len( stringLine ) == 0:
            raise WireException( "Received invalid, empty message" )

        return stringLine

    async def _processMessage( self, msg ):
        log = self._log

        if isinstance( msg, Exception ):
            Connection._callListener( self._onException, self )

        elif isinstance( msg, Ping ):
            await self._writer.drain( )
            self._writer.write( Pong.toWire( ) )

        elif isinstance( msg, Disconnect ):
            await Connection._callListener( self._onDisconnected, self )

        elif isinstance( msg, Pong ):
            pass

        else:
            errorMsg = "Internal error in '_process': Unknown message type"
            log.error( errorMsg )
            await Connection._callListener( self._onException, self, Exception( errorMsg ) )

    def _fromWire( self, line: str ):
        if line == "I":
            return Ping( )
        elif line == "O":
            return Pong( )
        elif line == "C":
            return Disconnect( )

        raise WireException( "Received invalid message" )

    async def _readTaskBody( self ):
        log = self._log

        while True:
            lineInBytes = await self._reader.readline( )
            self._dataReceived = True

            try:
                line = Connection._stripFromWire( lineInBytes )
                message = self._fromWire( line )
            except Exception as e:
                message = e

            await self._processMessage( message )

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


__all__ = ( "Connection", )
