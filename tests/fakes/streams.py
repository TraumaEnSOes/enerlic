import asyncio


class FakeReader:
    def __init__( self ):
        self.queue = asyncio.Queue( )
        self._closed = False

    async def close( self ):
        self._closed = True
        await self.queue.put( 0 )

    async def readline( self ) -> bytes:
        if self._closed: return b""
        else:
            value = await self.queue.get( )
            return b"" if self._closed else value

    async def write( self, line ):
        await self.queue.put( line )


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