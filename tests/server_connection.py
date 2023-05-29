import asyncio
import unittest
import os
import sys


if __name__ == "__main__":
    srcPath = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    srcPath = os.path.join( srcPath, "src" )

    sys.path.append( srcPath )


from enerlic.server_connection import *
from fakes.streams import *
from utils.connection import TestConnection


class TestServerConnection( unittest.IsolatedAsyncioTestCase, TestConnection ):
    async def test_user_message( self ):
        """
        A client did send a message to this server

        The signal onUserMessage must be emitted
        """
        outputList = [ ]

        async def slotOnUserMessage( connection, text ):
            nonlocal outputList

            outputList.append( ( connection.id, text, ) )

        reader = FakeReader( )
        writer = FakeWriter( )
        conn = ServerConnection( reader, writer, "0.0.0.0:0" )

        conn.onUserMessage( slotOnUserMessage )
        conn.run( )

        await reader.write( b"@Hello World!\n" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )

        assert len( outputList ) == 1
        assert len( outputList[0] ) == 2
        assert outputList[0][0] == "0.0.0.0:0"
        assert outputList[0][1] == "Hello World!"

    async def test_send_text( self ):
        """
        The server send a message to this client.
        
        The message must be written over the socket in the right binary format.
        """
        reader = FakeReader( )
        writer = FakeWriter( )
        conn = ServerConnection( reader, writer, "0.0.0.0:0" )

        conn.run( )

        await conn.sendText( conn.idInBytes, "hello world!" )
        await asyncio.sleep( 0.0 )

        await conn.stop( )
    
        assert len( writer.wire ) == 1
        assert writer.wire[0] == b"@0.0.0.0:0 hello world!\n"


if __name__ == "__main__":
    unittest.main( )
