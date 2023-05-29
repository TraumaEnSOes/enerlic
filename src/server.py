import argparse
import asyncio
import logging
import logging.config


from enerlic.router import Router
from enerlic.server_connection import ServerConnection


DEFAULT_PORT = 4444
DEFAULT_LOG_FILE = "enerlic.log"


def ParseCli( argv = None ):
    parser = argparse.ArgumentParser( )
    parser.add_argument( "-p", "--port", metavar = "<Port>", type = int, default = 4444, dest = "port", help = f"Port to listener (default {DEFAULT_PORT})" )
    parser.add_argument( "-l", "--log", metavar = "<LogFile>", default = DEFAULT_LOG_FILE, dest = "logFile", help = f"Log file (default {DEFAULT_LOG_FILE})" )

    args = parser.parse_args( ) if argv is None else parser.parse_args( argv )

    return args


async def mainLoop( port: int, router: Router ) -> None:
    async def newConnectionHandler( reader, writer ):
        id = writer.get_extra_info('peername')
        id = id[0] + ":" + str( id[1] )
        client = ServerConnection( reader, writer, id )

        router.addClient( client )

        client.run( )

        print( "New client added:", id )

    async def clientDisconnected( client ):
        print( "Client disconnected:", client.id, flush = True )

    asyncServer = await asyncio.start_server( newConnectionHandler, "0.0.0.0", port )
    addrs = ", ".join( str( sock.getsockname( ) ) for sock in asyncServer.sockets )
    print( f"Server started, listening on {addrs}" )

    async with asyncServer:
        await asyncServer.serve_forever( )


async def main( ):
    cliArgs = ParseCli( )
    logFile = open( cliArgs.logFile, "w" )
    router = Router( logFile )

    await mainLoop( cliArgs.port, router )    


if __name__ == "__main__":
    asyncio.run( main( ) )
