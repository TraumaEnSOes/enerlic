import asyncio
import copy
import logging
import time
import sys


from .server_connection import *


class Router:
    """
    Routing messages between clients.
    Also saves messages to file
    """
    def __init__( self, logStream ):
        self._log = logStream
        self._clients: dict[str, ServerConnection] = { }
        self._queue = asyncio.Queue( )
        self._task = asyncio.create_task( self._taskBody( ) )

        self._onDisconnected = None

    def addClient( self, conn: ServerConnection ) -> None:
        """
        Add a new client.
        """
        conn.onStop( self._slotDisconnection )
        conn.onUserMessage( self._slotUserMessage )
        self._clients[conn.id] = conn

    def onDisconnected( self, target = None ):
        """
        Signal emitted when a client disconnects
        """
        self._onDisconnected = target

    def clientsIds( self ):
        """
        Returns a list of the IDs of all active clients.
        """
        return copy.deepcopy( list( self._clients.keys( ) ) )

    async def stop( self ):
        """
        Stops this router. No more signals, no more message routing.
        Closes all active clients.
        Clear the list of actives clients.
        """
        if self._task is not None:
            self._task.cancel( )
            for conn in self._clients.values( ):
                conn.onStop( )
                await conn.stop( )

            self._clients = { }

    async def _taskBody( self ):
        """
        Main loop.
        Wait messages from clients and routing them.
        """
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
        """
        Listener of the 'onUserMessage' signal of any active client.
        Saves message into the log file.
        Queue message for main loop to process.
        """
        now = "0000" + str( round( time.time( ) * 1000 ) )
        now = now[-8:]

        print( f"[{now}] {conn.id} {text}", file = self._log, flush = True )
        await self._queue.put( ( conn, text, ) )
    
    async def _slotDisconnection( self, conn ):
        """
        Listener of the 'onStop' signal of any active client.
        Remove the client from the active clients list.
        """
        await Connection._callListener( self._onDisconnected, conn )
        del self._clients[conn.id]
