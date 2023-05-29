import asyncio


class FakeServerConnection:
    def __init__( self, id: bytes | str ):
        self._running = False

        if isinstance( id, str ):
            self._id = id
            self._idInBytes = id.encode( )
        else:
            self._idInBytes = id
            self._id = id.decode( )

        self._onStop = None        
        self._onUserMessage = None

    def run( self ):
        self._running = True

    def onStop( self, target = None ):
        self._onStop = target

    def onUserMessage( self, target = None ):
        self._onUserMessage = target

    @staticmethod
    async def _callListener( target, *args, **kargs ):
        if target is not None:
            if asyncio.iscoroutinefunction( target ):
                await target( *args, **kargs )
            else:
                target( *args, **kargs )


    def fakeStop( self ):
        FakeServerConnection._callListener( self._onStop, self )

    def fakeUserMessage( self, text ):
        FakeServerConnection._callListener( self._onUserMessage, self, text )
