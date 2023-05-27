import asyncio
import logging


from .server_connection import *


class Router:
    def __init__( self ):
        self._log = logging.getLogger( "crupier" )
        self._clients: dict[str, ServerConnection] = { }

    def addClient( self, conn: ServerConnection ) -> None:
        conn.onException( self._slotException )
        conn.onStop( self._slotDisconnection )
        conn.onUserMessage( self._slotUserMessage )
        self._clients[conn.id] = conn

    def removeClient( self, conn: ServerConnection ) -> None:
        conn.onException( None )
        conn.onStop( None )
        conn.onUserMessage( None )
        internalConn = self._clients.get( conn.id )

        if internalConn is not None:
            del self._clients[conn.id]

    async def _sendToAll( self, command, ignoreConnId: str = "" ) -> None:
        if len( ignoreConnId ):
            for c in self._clients.values( ):
                if c.id != ignoreConnId:
                    await c.processCommand( command )        
        else:
            for c in self._clients.values( ):
                c.processCommand( command )

    async def _slotUserMessage( self, conn: ServerConnection, text: str ) -> None:
        if len( text ):
            command = SendTextCommand( conn.idInBytes, text )
            await self._sendToAll( command, conn.id )

    async def _slotException( self, conn: ServerConnection ):
        pass

    async def _slotDisconnection( self, conn ):
        pass

