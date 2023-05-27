from collections import deque as Deque


class FakeReader:
    def __init__( self ):
        self.queue = Deque( )
        self._closed = False

    def close( self ):
        self._closed = True

    async def readline( self ):
        return "" if self._closed else self.queue.popleft( )

    async def write( self, line ):
        self.queue.append( line )


class FakeWriter:
    def __init__( self ):
        self.queue = Deque( )
        self.closed = False

    def close( self ):
        self.closed = True

    def write( self, data ):
        self.queue.append( data )

    async def drain( self ):
        return

    async def wait_closed( self ):
        return