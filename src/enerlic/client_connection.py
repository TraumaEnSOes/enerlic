from .connection import *

class UserMessage:
    def __init__( self, sender: str, text: str ):
        self.sender = sender
        self.text = text

class ClientConnection( Connection ):
    """
    Connection, from the point of view of a client (with the server)
    """
    def __init__( self, reader, writer ):
        super( ).__init__( reader, writer )

    def onUserMessage( self, target = None ) -> None:
        """
        Signal emmited when a user message arrives.
        """
        self._onUserMessage = target

    async def sendText( self, data: str | bytes ):
        """
        Send a user message over the socket.
        """
        data = Connection._stripDataToSend( data )

        if len( data ):
            wireData = b"@" + data
            self._writer.write( wireData )
            await self._writer.drain( )

    def _parseMessagefromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException | UserMessage:
        """
        Parse the reception of a user message
        """
        if len( line ) and line[0] == "@":
            sepPos = line.index( " " )
            return UserMessage( line[1:sepPos], line[sepPos + 1:] )
        else:
            return super( )._parseMessagefromWire( line )

    async def _processMessage( self, msg ) -> None:
        """
        Process a user message.
        """
        if isinstance( msg, UserMessage ):
            await Connection._callListener( self._onUserMessage, self, msg.sender, msg.text )
        else:
            await super( )._processMessage( msg )
        

    def clearListeners( self ) -> None:
        """
        Clear the 'userMessage' listener
        """
        self._onUserMessage = None
        super( ).clearListeners( )
