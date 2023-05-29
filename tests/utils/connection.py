import asyncio
import unittest
import os
import sys


from enerlic.connection import Connection, Ping, Pong, WireException
from fakes.streams import *


class TestConnection:
    async def test_run_stop( self ):
        stopCount = 0

        def slotStop( connection ):
            nonlocal stopCount

            stopCount += 1

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        assert conn.dataReceived( ) == False
        assert conn.running( ) == False

        conn.onStop( slotStop )
        conn.run( )
        assert conn.running( ) == True

        await conn.stop( )
        await asyncio.sleep( 0.0 )

        assert conn.running( ) == False
        assert stopCount == 1

    async def test_disconnect( self ):
        stopCount = 0

        def slotStop( connection ):
            nonlocal stopCount

            stopCount += 1

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onStop( slotStop )
        conn.run( )

        await reader.close( )
        await asyncio.sleep( 0.0 )

        assert stopCount == 1

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

        assert len( writer.wire ) == 1
        assert writer.wire[0] == Pong.toWire( )
        assert conn.running( ) == False

    async def test_disconnected( self ):
        stopCount = 0

        def slotStop( connection ):
            nonlocal stopCount

            stopCount += 1

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onStop( slotStop )

        conn.run( )
        await reader.close( )
        await asyncio.sleep( 0.0 )

        assert stopCount == 1
        assert conn.running( ) == False

    async def test_bad_wire( self ):
        errsList = [ ]

        def slotException( connection, err ):
            nonlocal errsList

            errsList.append( err )

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onException( slotException )

        conn.run( )
        await reader.write( b"aaaaa\n" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert len( errsList ) == 1
        assert isinstance( errsList[0], WireException )
