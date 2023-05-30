import asyncio
import io
import unittest
import os
import sys


if __name__ == "__main__":
    srcPath = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    srcPath = os.path.join( srcPath, "src" )

    sys.path.append( srcPath )


from fakes.server_connection import FakeServerConnection
from enerlic.router import Router


class TestRouter( unittest.IsolatedAsyncioTestCase ):
    async def test_client_disconnected( self ):
        """
        A client did disconnect from this server.

        The signal onDisconnected must be emitted.
        The client must be deleted from the active clients list.
        """
        disconnections = 0

        def slotDisconnected( conn ):
            nonlocal disconnections

            disconnections += 1

        logStream = io.StringIO( )
        router = Router( logStream )
        router.onDisconnected( slotDisconnected )

        assert len( router.clientsIds( ) ) == 0

        client1 = FakeServerConnection( 'fake1' )

        router.addClient( client1 )

        assert len( router.clientsIds( ) ) == 1
        assert router.clientsIds( )[0] == "fake1"
        assert disconnections == 0

        await client1.fakeStop( )
        await asyncio.sleep( 0.0 )

        assert disconnections == 1
        assert len( router.clientsIds( ) ) == 0

        logLines = logStream.readline( )

        assert len( logLines ) == 0

    async def test_single_client( self ):
        """
        Only one connected client.

        When a message arrives, it must be not forwarded to the client itself.
        """
        logStream = io.StringIO( )
        router = Router( logStream )

        client1 = FakeServerConnection( "fake1" )

        router.addClient( client1 )

        await client1.fakeUserMessage( "Fake text" )
        await asyncio.sleep( 0.0 )
        await router.stop( )
        await asyncio.sleep( 0.0 )

        assert len( client1.textSent ) == 0

    async def test_2_clients( self ):
        """
        Two connected clients.

        When a message arrives, it must be forwarded to the other client.
        """
        logStream = io.StringIO( )
        router = Router( logStream )

        client1 = FakeServerConnection( "fake1" )
        client2 = FakeServerConnection( "fake2" )

        router.addClient( client1 )
        router.addClient( client2 )

        await client1.fakeUserMessage( "Fake text from client1" )
        await asyncio.sleep( 0.0 )
        await client2.fakeUserMessage( "Fake text from client2" )
        await asyncio.sleep( 0.0 )
        await router.stop( )
        await asyncio.sleep( 0.0 )

        assert len( client1.textSent ) == 1
        assert client1.textSent[0][0] == b"fake2"
        assert client1.textSent[0][1] == "Fake text from client2"
        assert len( client2.textSent ) == 1
        assert client2.textSent[0][0] == b"fake1"
        assert client2.textSent[0][1] == "Fake text from client1"

    async def test_3_clients( self ):
        """
        Three connected clients.

        When a message arrives, it must be forwarded to the others clients.

        THE ORDER OF THE FORWARD IS IMPLEMENTATION-DEPENDENT !!!
        """
        logStream = io.StringIO( )
        router = Router( logStream )

        client1 = FakeServerConnection( "fake1" )
        client2 = FakeServerConnection( "fake2" )
        client3 = FakeServerConnection( "fake3" )

        router.addClient( client1 )
        router.addClient( client2 )
        router.addClient( client3 )

        await client1.fakeUserMessage( "Fake text from client1" )
        await asyncio.sleep( 0.0 )
        await client2.fakeUserMessage( "Fake text from client2" )
        await asyncio.sleep( 0.0 )
        await client3.fakeUserMessage( "Fake text from client3" )
        await asyncio.sleep( 0.0 )
        await router.stop( )
        await asyncio.sleep( 0.0 )

        assert len( client1.textSent ) == 2
        assert client1.textSent[0][0] == b"fake2"
        assert client1.textSent[0][1] == "Fake text from client2"
        assert client1.textSent[1][0] == b"fake3"
        assert client1.textSent[1][1] == "Fake text from client3"
        assert len( client2.textSent ) == 2
        assert client2.textSent[0][0] == b"fake1"
        assert client2.textSent[0][1] == "Fake text from client1"
        assert client2.textSent[1][0] == b"fake3"
        assert client2.textSent[1][1] == "Fake text from client3"
        assert len( client3.textSent ) == 2
        assert client3.textSent[0][0] == b"fake1"
        assert client3.textSent[0][1] == "Fake text from client1"
        assert client3.textSent[1][0] == b"fake2"
        assert client3.textSent[1][1] == "Fake text from client2"


if __name__ == "__main__":
    unittest.main( )
