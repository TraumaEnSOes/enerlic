import asyncio
import copy
import logging
import time
import sys


from .server_connection import *


class Router:
    def __init__( self, logStream ):
        self._log = logStream
        self._clients: dict[str, ServerConnection] = { }
        self._queue = asyncio.Queue( )
        self._task = asyncio.create_task( self._taskBody( ) )

        self._onDisconnected = None

    def addClient( self, conn: ServerConnection ) -> None:
        conn.onStop( self._slotDisconnection )
        conn.onUserMessage( self._slotUserMessage )
        self._clients[conn.id] = conn

    def onDisconnected( self, target = None ):
        self._onDisconnected = target

    def clientsIds( self ):
        return copy.deepcopy( list( self._clients.keys( ) ) )

    async def stop( self ):
        if self._task is not None:
            self._task.cancel( )
            for conn in self._clients.values( ):
                await conn.stop( )

            self._clients = { }

    async def _taskBody( self ):
        while True:
            message = await self._queue.get( )
    
            sender = message[0]
            senderId = sender.id
            text = message[1]
            clients = copy.deepcopy( tuple( self._clients.keys( ) ) )

            for clientId in clients:
                if clientId != sender.id:
                    client = self._clients.get( clientId )

                    if client is not None:
                        await client.sendText( sender.idInBytes, text )

    async def _slotUserMessage( self, conn: ServerConnection, text: str ) -> None:
        now = "0000" + str( round( time.time( ) * 1000 ) )
        now = now[-8:]

        print( f"[{now}] {conn.id} {text}", file = self._log, flush = True )
        await self._queue.put( ( conn, text, ) )
    
    async def _slotDisconnection( self, conn ):
        await Connection._callListener( self._onDisconnected, conn )
        del self._clients[conn.id]
