import asyncio
import unittest
import os
import sys


from fakes import *


class TestConnection( unittest.IsolatedAsyncioTestCase ):
    async def test_constructor( self ):
        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        assert conn.dataReceived( ) == False

    async def test_ping_pong( self ):
        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )
        conn.run( )

        await reader.write( Ping.toWire( ) )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert writer.closed == True
        assert conn.dataReceived( ) == True

        data = writer.queue.popleft( )
        assert data == Pong.toWire( )

    async def test_closed( self ):
        sentData = [ ]

        def dataReceived( connection ):
            sentData.append( connection )

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onDisconnected( dataReceived )

        conn.run( )
        await reader.write( b"C\n" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert len( sentData ) == 1
        assert sentData[0] == conn

    async def test_bad_wire( self ):
        sentData = [ ]

        def dataReceived( connection, err ):
            sentData.append( err )

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onException( dataReceived )

        conn.run( )
        await reader.write( b"\n" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert len( sentData ) == 1
        assert isinstance( sentData[1], WireException )


if __name__ == "__main__":
    srcPath = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    srcPath = os.path.join( srcPath, "src" )

    sys.path.append( srcPath )

    from enerlic.connection import Connection, Ping, Pong, WireException

    unittest.main( )
