from enerlic.server_connection import *


class FakeServerConnection( ServerConnection ):
    def __init__( self, reader, writer, id: str | bytes ):
        super( ).__init__( reader, writer, id )
        self.commandsList = [ ]

    async def processCommand( self, command ):
        self.commandsList.append( command )
