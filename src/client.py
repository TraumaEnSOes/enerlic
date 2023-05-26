import argparse
import asyncio
import logging
import logging.config


from enerlic.client import Client


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


def ParseCli( argv = None ):
    parser = argparse.ArgumentParser( )
    parser.add_argument( "-d", "--debug", action = "store_true", dest = "debug", help = "Enable debug (log all to console)" )
    parser.add_argument( "-t", "--timeout", metavar = "<Timeout>", type = int, default = DEFAULT_TIMEOUT, dest = "timeout", help = f"Client timeout in seconds (default {DEFAULT_TIMEOUT})" )
    parser.add_argument( metavar = "<Server>", nargs = "?", dest = "server", default = DEFAULT_SERVER, help = f"Server IP or DNS to connect (default {DEFAULT_SERVER})" )
    parser.add_argument( metavar = "<Port>", type = int, nargs = "?", default = 4444, dest = "port", help = f"Port to listener (default {DEFAULT_PORT})" )

    args = parser.parse_args( ) if argv is None else parser.parse_args( argv )

    return args


def SetupLogger( debugMode: bool ):
    if debugMode:
        LOG_CONFIG["loggers"][""]["level"] = "DEBUG"
        LOG_CONFIG["loggers"]["connection"]["level"] = "DEBUG"

    return logging.config.dictConfig( LOG_CONFIG )


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')

    print(f"Received {message!r} from {addr!r}")

    print(f"Send: {message!r}")
    writer.write(data)
    await writer.drain()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main( ):
    cliArgs = ParseCli( )
    SetupLogger( cliArgs.debug )

    asyncClient = Client( cliArgs.server, cliArgs.port, cliArgs.timeout )
    await asyncClient.run( )


if __name__ == "__main__":
    asyncio.run( main( ) )
