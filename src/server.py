import argparse
import asyncio
import logging
import logging.config


from enerlic.server import Server


DEFAULT_PORT = 4444
DEFAULT_TIMEOUT = 60
DEFAULT_LOG_FILE = "enerlic.log"

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
        },
        "file": { 
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "maxBytes": 16384,
            "backupCount": 3,
            "filename": None
        }
    },
    "loggers": { 
        "": {  # root logger
            "handlers": [ "file" ],
            "level": "DEBUG",
            "propagate": False
        },
        "server": {
            "handlers": [ "file" ],
            "level": "DEBUG",
            "propagate": False
        },
        "connection": {
            "handlers": [ "file" ],
            "level": "DEBUG",
            "propagate": False
        }
    }
}


def ParseCli( argv = None ):
    parser = argparse.ArgumentParser( )
    parser.add_argument( "-p", "--port", metavar = "<Port>", type = int, default = 4444, dest = "port", help = f"Port to listener (default {DEFAULT_PORT})" )
    parser.add_argument( "-t", "--timeout", metavar = "<Timeout>", type = int, default = DEFAULT_TIMEOUT, dest = "timeout", help = f"Client timeout in seconds (default {DEFAULT_TIMEOUT})" )
    parser.add_argument( "-l", "--log", metavar = "<LogFile>", default = DEFAULT_LOG_FILE, dest = "logFile", help = f"Log file (default {DEFAULT_LOG_FILE})" )
    parser.add_argument( "-d", "--debug", action = "store_true", dest = "debug", help = "Enable debug (log all to console)" )

    args = parser.parse_args( ) if argv is None else parser.parse_args( argv )

    return args


def SetupLogger( logFile: str, debugMode: bool ) -> logging.Logger:
    LOG_CONFIG["handlers"]["file"]["filename"] = logFile

    if debugMode:
        LOG_CONFIG["loggers"][""]["handlers"].append( "console" )
        LOG_CONFIG["loggers"]["server"]["handlers"].append( "console" )
        LOG_CONFIG["loggers"]["connection"]["handlers"].append( "console" )

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
    SetupLogger( cliArgs.logFile, cliArgs.debug )

    serverInstance = Server( cliArgs.port )
    serverTask = asyncio.create_task( serverInstance.run( ) )

    asyncServer = await asyncio.start_server( serverInstance.newConnection, "0.0.0.0", cliArgs.port )

    addrs = ", ".join( str( sock.getsockname( ) ) for sock in asyncServer.sockets )
    print( f"Server started, listening on {addrs}" )

    async with asyncServer:
        await asyncServer.serve_forever( )

if __name__ == "__main__":
    asyncio.run( main( ) )
