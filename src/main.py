#!/usr/bin/env python3

"""
This module starts the server and completes initialisation
"""

# installed modules
from aiohttp import web

# custom modules
import logger as Logger
import router as Router


# start the server if this file is executed
if __name__ == '__main__':
    # this should be set in an environment variable
    LISTEN_PORT = 12021

    APP = web.Application()
    APP.add_routes([web.route('*', r'/{tail:.*}', Router.entry_point)])

    Logger.log_info("Server startup")
    web.run_app(APP, port=LISTEN_PORT)
