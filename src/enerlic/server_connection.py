import asyncio


from .connection import Connection


class UserMessage:
    def __init__( self, sender: str, text: str ):
        self.sender = sender
        self.text = text


class ServerConnection( Connection ):
    def __init__( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, id: str | bytes ):
        super( ).__init__( reader, writer )

        if isinstance( id, str ):
            self._id = id
            self._idInBytes = id.encode( )
        else:
            self._id = id.decode( )
            self._idInBytes = id

    @property
    def id( self ):
        return self._id

    @property
    def idInBytes( self ):
        return self._idInBytes

    def onUserMessage( self, target = None ) -> None:
        self._onUserMessage = target

    async def sendText( self, sender: bytes, data: str | bytes ) -> None:
        data = super( )._stripDataToSend( data )

        if data is not None:
            wireData = b"@" + sender + " " + data
            await self._writer.drain( )
            self._writer.write( wireData )

    async def _fromWire( self, line: str ) -> UserMessage:
        if line[0] != "@":
            return await super( )._fromWire( line )

        sepPos = str.index( " " )

        return UserMessage( line[1:sepPos], line[sepPos + 1:] )

    async def _processMessage( self, msg ) -> None:
        if not isinstance( msg, UserMessage ):
            await super( )._processMessage( msg )

        await Connection._callListener( self._onUserMessage, )

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
