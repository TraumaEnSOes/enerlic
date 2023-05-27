import asyncio


from .connection import *


class UserMessage:
    def __init__( self, text: str ):
        self.text = text


class SendTextCommand:
    def __init__( self, sender: bytes, text: str ):
        self._raw = b"@" + sender + b" " + text.encode( )

    def toWire( self ) -> bytes:
        return self._raw


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

    async def processCommand( self, command ) -> None:
        if isinstance( command, SendTextCommand ):
            await self._writer.drain( )
            self._writer.write( command.toWire( ) )
        else:
            raise Exception( "Internal error: unknown command" )

    async def _parseMessageFromWire( self, line: str ) -> Ping | Pong | Disconnected | WireException | UserMessage:
        if line[0] == "@":
            return UserMessage( line[1:] )
        else:
            return await super( )._parseMessagefromWire( line )

    async def _processMessage( self, msg ) -> None:
        if isinstance( msg, UserMessage ):
            await Connection._callListener( self._onUserMessage, self, msg.text )
        else:
            await super( )._processMessage( msg )

    def clearListeners( self ) -> None:
        self._onUserMessage = None
        super( ).clearListeners( )
