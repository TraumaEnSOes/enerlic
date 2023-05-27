import unittest
import os
import sys


if __name__ == "__main__":
    srcPath = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
    srcPath = os.path.join( srcPath, "src" )

    sys.path.append( srcPath )


from fakes.streams import *
from fakes.server_connection import FakeServerConnection


class TestRouter( unittest.IsolatedAsyncioTestCase ):
    async def test_single_client( self ):
        pass

    async def test_many_clients( self ):
        pass


if __name__ == "__main__":
    unittest.main( )
