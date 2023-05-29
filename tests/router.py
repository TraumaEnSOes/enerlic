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
    async def test_basic( self ):
        disconnections = 0

        def slotDisconnected( conn ):
            nonlocal disconnections

            disconnections += 1

        logStream = io.StringIO( )
        router = Router( logStream )

        assert len( router.clientsIds( ) ) == 0

        client1 = FakeServerConnection( 'fake1' )

        router.addClient( client1 )
        asyncio.sleep( 0.0 )

        assert len( router.clientsIds( ) ) == 1
        assert router.clientsIds( )[0] == "fake1"
        assert disconnections == 0

        client1.fakeStop( )
        asyncio.sleep( 0.0 )

        assert disconnections == 1
        assert len( router.clientsIds( ) ) == 0


if __name__ == "__main__":
    unittest.main( )
