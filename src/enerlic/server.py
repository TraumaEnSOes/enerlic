import asyncio
import logging


from .server_connection import ServerConnection


class Server:
    def __init__( self ):
        self._clients = { }
        self._log = logging.getLogger( "server" )

    def onException( self, target = None ) -> None:
        self._onException = target

    async def appendClient( self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter ) -> str:
        log = self._log

        id = writer.get_extra_info( "peername" )
        id = id[0] + ":" + str( id[1] )

        conn = ServerConnection( reader, writer, id )

        conn.onDisconnected( self._slotDisconnected )
        conn.onException( self._slotException )
        conn.onUserMessage( self._slotUserMessage )

        self._clients[id] = conn

        conn.run( )

        log.debug( f"<{id}> client added" )

    async def stopClient( self, id ):
        log = self._log

        conn = self._clients[id]

        await conn.notifyDisconnection( )
        await conn.stop( )

        del self._clients[id]

        log.debug( f"<{id}> client disconnected" )

    async def stopAll( self ):
        self._log.debug( "Disconnecting all clients ..." )

        for conn in self._clients.values( ):
            await conn.notifyDisconnection( )
            await conn.stop( )

        self._clients = { }

    @property
    def connections( self ):
        return len( self._clients )

    async def _slotDisconnected( self, connection ):
        pass

    async def _slotException( self, connection, err ):
        pass

    async def _slotUserMessage( self, connection, text )