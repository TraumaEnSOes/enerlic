from collections import deque as Deque


class FakeReader:
    def __init__( self ):
        self.queue = Deque( )
        self._closed = False

    def close( self ):
        self._closed = True

    async def readline( self ) -> bytes:
        if self._closed:
            return b""
        elif len( self.queue ) == 0:
            return b"P\n"
        else:
            return self.queue.popleft( )

    async def write( self, line ):
        self.queue.append( line )


class FakeWriter:
    def __init__( self ):
        self.wire = [ ]
        self.closed = False

    def close( self ):
        self.closed = True

    def write( self, data ):
        self.wire.append( data )

    async def drain( self ):
        return

    async def wait_closed( self ):
        return