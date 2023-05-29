import asyncio
import unittest
import os
import sys


from enerlic.connection import Connection, Ping, Pong, WireException
from fakes.streams import *


class TestConnection:
    async def test_run_stop( self ):
        """
        Basic operation: start and stop a socket.
  
        Before run( ): running must be False
        After run( ): running must be True
        After stop( ): running must be False
                       signal onStop must be emitted
        """
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
        """
        The peer close the socket

        Signal onStop must be emitted
        """
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
        """
        If the socket receives a Ping, it must be respons with a Pong

        Before the Ping, dataReceived( ) must returns False
        After the Ping, dataReceived( ) must returns True
        """
        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )
        conn.run( )

        assert conn.dataReceived( ) == False
        await reader.write( Ping.toWire( ) )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert writer.closed == True
        assert conn.dataReceived( ) == True

        assert len( writer.wire ) == 1
        assert writer.wire[0] == Pong.toWire( )

    async def test_bad_wire( self ):
        """
        Invalid message received from the socket.

        Socket must be auto-close
        Signal onException must be emitted
        Signal onStop must be emitted
        """
        errsList = [ ]
        stopCount = 0

        def slotException( connection, err ):
            nonlocal errsList

            errsList.append( err )

        def slotStop( connection ):
            nonlocal stopCount

            stopCount += 1

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = Connection( reader, writer )

        conn.onException( slotException )
        conn.onStop( slotStop )

        conn.run( )
        await reader.write( b"aaaaa\n" )
        await asyncio.sleep( 0.0 )

        assert conn.running( ) == False
        assert stopCount == 1
        assert len( errsList ) == 1
        assert isinstance( errsList[0], WireException )
