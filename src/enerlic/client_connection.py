from .connection import *

class UserMessage:
    def __init__( self, sender: str, text: str ):
        self.sender = sender
        self.text = text

class ClientConnection( Connection ):
    def __init__( self, reader, writer ):
        super( ).__init__( reader, writer )

    def onUserMessage( self, target = None ) -> None:
        self._onUserMessage = target

    async def sendText( self, data: str | bytes ):
        data = Connection._stripDataToSend( data )

        if len( data ):
            wireData = b"@" + data
            self._writer.write( wireData )
            await self._writer.drain( )

    def _parseMessagefromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException | UserMessage:
        if line[0] == "@":
            sepPos = line.index( " " )
            return UserMessage( line[1:sepPos], line[sepPos + 1:] )
        else:
            return super( )._parseMessageFromWire( line )

    async def _processMessage( self, msg ) -> None:
        if isinstance( msg, UserMessage ):
            await Connection._callListener( self._onUserMessage, self, msg.sender, msg.text )
        else:
            await super( )._processMessage( msg )
        

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
