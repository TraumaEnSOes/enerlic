from .connection import Connection

class UserMessage:
    def __init__( self, sender: str, text: str ):
        self.sender = sender
        self.text = text

class ClientConnection( Connection ):
    def __init__( self, reader, writer ):
        super( ).__init__( reader, writer )

    async def sendText( self, data: str | bytes ):
        data = super( )._verifyDataToSend( data )

        if data is not None:
            wireData = "@" + data
            await self._writer.drain( )
            self._writer.write( wireData )

    async def _fromWire( self, line: str ):
        if line[0] != "@":
            return await super( )._fromWire( line )

        sepPos = str.index( " " )
        return UserMessage( line[1:sepPos], line[sepPos + 1:] )

    async def _processMessage( self, msg ) -> None:
        if not isinstance( msg, UserMessage ):
            await super( )._processMessage( msg )

        Connection._callListener( self._onUserMessage, )

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
