import argparse
import asyncio
#import curses
import logging.config
import sys


from enerlic import ClientConnection


DEFAULT_PORT = 4444
DEFAULT_TIMEOUT = 5
DEFAULT_SERVER = "127.0.0.1"

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": { 
        "standard": { 
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": { 
        "console": { 
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        }
    },
    "loggers": {
        "": {
            "handlers": [ "console" ],
            "level": "INFO",
            "propagate": False
        },
        "connection": {
            "handlers": [ "console" ],
            "level": "INFO",
            "propagate": False
        }
    }
}


log = None

async def connectStdInOut( ):
    loop = asyncio.get_event_loop( )
    reader = asyncio.StreamReader( )
    protocol = asyncio.StreamReaderProtocol( reader )
    await loop.connect_read_pipe( lambda: protocol, sys.stdin )
    w_transport, w_protocol = await loop.connect_write_pipe( asyncio.streams.FlowControlMixin, sys.stdout )
    writer = asyncio.StreamWriter( w_transport, w_protocol, reader, loop )
    return reader, writer


def parseCli( argv = None ):
    parser = argparse.ArgumentParser( )
    parser.add_argument( "-d", "--debug", action = "store_true", dest = "debug", help = "Enable debug (log all to console)" )
    parser.add_argument( "-t", "--timeout", metavar = "<Timeout>", type = int, default = DEFAULT_TIMEOUT, dest = "timeout", help = f"Client timeout in seconds (default {DEFAULT_TIMEOUT})" )
    parser.add_argument( metavar = "<Server>", nargs = "?", dest = "server", default = DEFAULT_SERVER, help = f"Server IP or DNS to connect (default {DEFAULT_SERVER})" )
    parser.add_argument( metavar = "<Port>", type = int, nargs = "?", default = 4444, dest = "port", help = f"Port to listener (default {DEFAULT_PORT})" )

    args = parser.parse_args( ) if argv is None else parser.parse_args( argv )

    if ( args.timeout < 5 ) or ( args.timeout > 300 ):
        print( "<Timeout> must be between 5 and 300, both included" )
        exit( 1 )

    return args


def setupLogger( debugMode: bool ):
    if debugMode:
        LOG_CONFIG["loggers"][""]["level"] = "DEBUG"
        LOG_CONFIG["loggers"]["connection"]["level"] = "DEBUG"

    logging.config.dictConfig( LOG_CONFIG )
    log = logging.getLogger( )


async def main( ) -> None:
    async def userMessageHandler( connection, sender, text ):
        await stdout.drain( )
        stdout.write( f"From {sender}: {text}" )

    cliArgs = parseCli( )
    setupLogger( cliArgs.debug )

    stdin, stdout = connectStdInOut( )
    reader, writer = await asyncio.open_connection( cliArgs.server, cliArgs.port )
    conn = ClientConnection( reader, writer )


if __name__ == "__main__":
    asyncio.run( main( None ) )
