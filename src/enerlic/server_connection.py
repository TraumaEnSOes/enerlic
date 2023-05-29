from .connection import *

class UserMessage:
    def __init__( self, text: str ):
        self.text = text

class ServerConnection( Connection ):
    def __init__( self, reader, writer, id: str | bytes ):
        super( ).__init__( reader, writer )

        if isinstance( id, str ):
            self._id = id
            self._idInBytes = id.encode( )
        else:
            self._idInBytes = id
            self._id = id.decode( )

    @property
    def id( self ):
        return self._id

    @property
    def idInBytes( self ):
        return self._idInBytes

    def onUserMessage( self, target = None ) -> None:
        self._onUserMessage = target

    async def sendText( self, sender: bytes, data: str | bytes ):
        data = Connection._stripDataToSend( data )

        if len( data ):
            wireData = b"@" + sender + b" " + data
            print( "to", self.id, wireData.decode( ), flush = True )
            self._writer.write( wireData )
            await self._writer.drain( )

    def _parseMessagefromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException | UserMessage:
        if len( line ) and ( line[0] == "@"):
            return UserMessage( line[1:] )
        else:
            return super( )._parseMessagefromWire( line )

    async def _processMessage( self, msg ) -> None:
        if isinstance( msg, UserMessage ):
            await Connection._callListener( self._onUserMessage, self, msg.text )
        else:
            await super( )._processMessage( msg )

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
