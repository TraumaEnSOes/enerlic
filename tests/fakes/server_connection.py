import asyncio


class FakeServerConnection:
    def __init__( self, id: bytes | str ):
        self.running = False

        if isinstance( id, str ):
            self._id = id
            self._idInBytes = id.encode( )
        else:
            self._idInBytes = id
            self._id = id.decode( )

        self._onStop = None        
        self._onUserMessage = None
        self.textSent = [ ]

    @property
    def id( self ):
        return self._id

    @property
    def idInBytes( self ):
        return self._idInBytes

    def run( self ):
        self.running = True

    def onStop( self, target = None ):
        self._onStop = target

    def onUserMessage( self, target = None ):
        self._onUserMessage = target

    async def stop( self ):
        self.running = False

    @staticmethod
    async def _callListener( target, *args, **kargs ):
        if target is not None:
            if asyncio.iscoroutinefunction( target ):
                await target( *args, **kargs )
            else:
                target( *args, **kargs )

    async def sendText( self, sender: bytes, data: str | bytes ):
        self.textSent.append( ( sender, data, ) )

    async def fakeStop( self ):
        await FakeServerConnection._callListener( self._onStop, self )

    async def fakeUserMessage( self, text: str ):
        await FakeServerConnection._callListener( self._onUserMessage, self, text )