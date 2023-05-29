import asyncio
import unittest
import os
import sys


if __name__ == "__main__":
    srcPath = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    srcPath = os.path.join( srcPath, "src" )

    sys.path.append( srcPath )


from enerlic.client_connection import *
from fakes.streams import *
from utils.connection import TestConnection


class TestClientConnection( unittest.IsolatedAsyncioTestCase, TestConnection ):
    async def test_user_message( self ):
        """
        The server did send a message to this client.

        The signal onUserMessage must be emitted
        """
        outputList = [ ]

        async def slotOnUserMessage( connection, sender, text ):
            nonlocal outputList

            outputList.append( ( connection, sender, text, ) )

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = ClientConnection( reader, writer )

        conn.onUserMessage( slotOnUserMessage )
        conn.run( )

        await reader.write( b"@0.0.0.0:0 Hello World!\n" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert len( outputList ) == 1
        assert len( outputList[0] ) == 3
        assert outputList[0][0] == conn
        assert outputList[0][1] == "0.0.0.0:0"
        assert outputList[0][2] == "Hello World!"

    async def test_send_text( self ):
        """
        This client send a message to the server.

        The message must be written over the socket in the right binary format.
        """
        reader = FakeReader( )
        writer = FakeWriter( )
        conn = ClientConnection( reader, writer )

        conn.run( )

        await conn.sendText( "hello world!")
        await asyncio.sleep( 0.0 )

        await conn.stop( )
    
        assert len( writer.wire ) == 1
        assert writer.wire[0] == b"@hello world!\n"


if __name__ == "__main__":
    unittest.main( )
