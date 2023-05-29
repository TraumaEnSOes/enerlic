import asyncio


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
    """
    Base class for all types of connections
    """
    def __init__( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter ):
        self._stop = True
        self._reader = reader
        self._writer = writer
        self._dataReceived = False

        self.clearListeners( )

    def run( self ):
        """
        Start listening on the socket
        """
        self._stop = False
        self._readTask = asyncio.create_task( self._readTaskBody( ) )

    def running( self ) -> bool:
        """
        Is this socket listening ?
        """
        return self._stop == False

    def onException( self, target = None ):
        """
        Signal emmited when an error occurs in this socket
        The closing of this socket is automatic
        """
        self._onException = target

    def onStop( self, target = None ):
        """
        Signal emmited when when this socket is closed
        After this, no more signals are emited
        """
        self._onStop = target

    def clearListeners( self ):
        """
        Clear all listeners, on all signals.
        """
        self._onException = None
        self._onStop = None

    def dataReceived( self ):
        """
        Returns True if this socket as received any data.
        """
        return self._dataReceived

    def clearDataReceived( self ):
        """
        Clear the internal 'dataReceived' flag.
        After call this, 'dataReceived( )' returns False until new data arrives
        """
        self._dataReceived = False

    async def ping( self ) -> None:
        """
        Send a Ping message over the socket
        """
        if self.running( ):
            await self._writer.drain( )
            self._writer.write( Ping.toWire( ) )

    async def stop( self ):
        """
        Stop the listening on this socket, and close it.
        Emit the 'onStop' signal.
        After this is called, no more signals are emitted, and the socket is closed.
        """
        if ( self._stop == False ) and ( self._readTask is not None ):
            self._stop = True
            await self._cleanup( )
            self._readTask.cancel( )

    #
    # Internal methods
    #
    @staticmethod
    async def _callListener( target, *args, **kargs ):
        """
        Emit a signal.
        """
        if target is not None:
            if asyncio.iscoroutinefunction( target ):
                await target( *args, **kargs )
            else:
                target( *args, **kargs )

    @staticmethod
    def _stripDataToSend( data: str | bytes ) -> bytes:
        """
        Removes leading and trailing spaces in a data, leaving it ready to be sent through the socket
        """
        if len( data ) == 0:
            return b""
            
        if isinstance( data, str ):
            data = data.encode( )

        data = data.strip( )

        if len( data ) == 0:
            return b""

        data = data + b"\n"

        return data

    async def _cleanup( self ):
        """
        Executed after the socket it's closed.
        Final steps on closing process.
        Child classes MUST NOT override it.
        """
        self._writer.close( )
        await self._writer.wait_closed( )
        await Connection._callListener( self._onStop, self )

    async def _processMessage( self, msg ) -> None:
        """
        Do actions when a new message arrives.
        It can be overwritten by child classes to append new functionality.
        """
        if isinstance( msg, Disconnected ):
            self._stop = True
        else:
            self._dataReceived = True

            if isinstance( msg, WireException ):
                self._stop = True
                await Connection._callListener( self._onException, self, msg )

            elif isinstance( msg, Ping ):
                self._writer.write( Pong.toWire( ) )
                await self._writer.drain( )

            elif isinstance( msg, Pong ):
                pass

            else:
                self._stop = True
                await Connection._callListener( self._onException, self, Exception( "Internal error in '_process': Unknown message type" ) )

    def _parseMessagefromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException:
        """
        Executed when a new message arrives over the socket.
        From raw data, it generate a valid message
        It can be overwritten by child classes to append new functionality.
        """
        if len( line ) == 0:
            return Disconnected( )
        elif line == "I":
            return Ping( )
        elif line == "O":
            return Pong( )
        else:
            return WireException( "Received invalid message" )

    async def _readTaskBody( self ) -> None:
        """
        Main loop of this socket.
        Gets lines from the sockets, and sends them to _parseMessageFromWire and _processMessage.
        Child classes MUST NOT override it.
        """
        try:
            while self._stop == False:
                lineInBytes = await self._reader.readline( )
                stringLine = "" if len( lineInBytes ) == 0 else lineInBytes.decode( ).strip( )

                message = self._parseMessagefromWire( stringLine )

                await self._processMessage( message )
        except asyncio.CancelledError:
            pass

        await self._cleanup( )

