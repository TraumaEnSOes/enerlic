from .connection import *

class UserMessage:
    def __init__( self, sender: str, text: str ):
        self.sender = sender
        self.text = text

class ClientConnection( Connection ):
    def __init__( self, reader, writer ):
        super( ).__init__( reader, writer )

    async def sendText( self, data: str | bytes ):
        data = Connection._stripDataToSend( data )

        if data is not None:
            wireData = "@" + data
            await self._writer.drain( )
            self._writer.write( wireData )

    async def _parseMessageFromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException | UserMessage:
        if line[0] == "@":
            sepPos = str.index( " " )
            return UserMessage( line[1:sepPos], line[sepPos + 1:] )
        else:
            return await super( )._parseMessageFromWire( line )

    async def _processMessage( self, msg ) -> None:
        if isinstance( msg, UserMessage ):
            await Connection._callListener( self._onUserMessage, msg.sender, msg.text )
        else:
            await super( )._processMessage( msg )
        

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
