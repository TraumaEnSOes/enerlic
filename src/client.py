import argparse
import asyncio
import typing
import sys

from enerlic.client_connection import ClientConnection


DEFAULT_PORT = 4444
DEFAULT_SERVER = "127.0.0.1"


async def connectStdIn( ) -> asyncio.StreamReader:
    """
    Returns a asyncio.StreamReader, to we can uses stdin with async methods.
    """
    loop = asyncio.get_event_loop( )
    reader = asyncio.StreamReader( )
    protocol = asyncio.StreamReaderProtocol( reader )
    await loop.connect_read_pipe( lambda: protocol, sys.stdin )
    return reader


def parseCli( argv = None ):
    parser = argparse.ArgumentParser( )
    parser.add_argument( metavar = "<Server>", nargs = "?", dest = "server", default = DEFAULT_SERVER, help = f"Server IP or DNS to connect (default {DEFAULT_SERVER})" )
    parser.add_argument( metavar = "<Port>", type = int, nargs = "?", default = 4444, dest = "port", help = f"Port to listener (default {DEFAULT_PORT})" )

    args = parser.parse_args( ) if argv is None else parser.parse_args( argv )

    return args


async def mainLoop( stdin: asyncio.StreamReader, connection: ClientConnection ) -> None:
    userInputTask: asyncio.Task = None

    async def clientDisconnected( connection ):
        nonlocal userInputTask

        userInputTask.cancel( )

    async def userMessageHandler( connection, sender, text ):
        print( f"From {sender}: {text}", flush = True )

    async def userInputTaskBody( ):
        nonlocal stdin, connection

        try:
            while True:
                text = await stdin.readline( )

                if text == b"@exit\n":
                    break
                else:
                    await connection.sendText( text )
        except asyncio.CancelledError:
            pass

    # Connect signals.
    connection.onUserMessage( userMessageHandler )
    connection.onStop( clientDisconnected )
    connection.run( )

    userInputTask = asyncio.create_task( userInputTaskBody( ) )
    
    await userInputTask
    print( "Finish" )


async def main( ) -> None:
    cliArgs = parseCli( )
    stdin = await connectStdIn( )
    reader, writer = await asyncio.open_connection( cliArgs.server, cliArgs.port )

    im = writer.get_extra_info( "sockname" )
    im = im[0] + ":" + str( im[1] )
    print( "I'm", im, flush = True )
    print( "Enter lines to send ('@exit' finish the program)" )

    conn = ClientConnection( reader, writer )

    await mainLoop( stdin, conn )


if __name__ == "__main__":
    asyncio.run( main( ) )
