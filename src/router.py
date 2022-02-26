#! /usr/bin/env python3
"""
This module handles routes all incoming requests to the appropriate modules.
General responses, like the options header, are also defined here
"""

# pylint: disable=broad-except

# default modules
import re

# installed modules
import aiohttp
from aiohttp import web

# custom modules
import logger as Logger
import jobs as Jobs


async def get_server_options_header() -> web.Response:
    """
    if OPTIONS request is received always respond with the headers below
    """
    options_header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': ('Content-Type, '
                                         'api_key, '
                                         'Content-Length, '
                                         'X-Requested-With, '
                                         'x-reset-id, '
                                         'x-reset-token')
    }

    return web.Response(
        status=200,
        headers=options_header
    )

JOB_START_REGEX = re.compile(r"^\/jobs(\/|\?|$)")


async def route_request(request: web.Request) -> web.Response:
    """
    Route the request to the appropriate handler funcion
    """
    try:
        request_path = request.path

        response = None
        if request.method == 'OPTIONS':
            response = await get_server_options_header()
        elif JOB_START_REGEX.match(request_path):
            response = await Jobs.router(request)
        else:
            Logger.log_error(
                f"User tried to access unused URL @ {request.path_qs}"
            )
            response = web.json_response(
                status=404,
                data={"error": "Not Found"}
            )

        return response

    except Exception as exc:
        Logger.log_exception(
            "Exeption caught in main router function",
            exc
        )
        raise


async def entry_point(request: web.Request) -> web.Response:
    """Entry point for all requests to the server"""
    try:
        Logger.log_info(
            f"Received {request.method} request to {request.path_qs}"
        )

        try:
            response = await route_request(request)

        except aiohttp.ServerTimeoutError:
            Logger.log_error(
                f"Request to {request.path_qs} caused the request to external service to timeout"
            )
            response = web.json_response(
                status=503,
                data={"error": "external service request timed out"}
            )

        except Exception as exc:
            Logger.log_exception(
                "Exeption caught in route_request coroutine",
                exc
            )
            response = web.json_response(
                status=500,
                data={"error": "Exception in request handler"}
            )

        if 200 <= response.status < 300:
            Logger.log_info(
                f"Success Code ({response.status})"
                f" returned with text ({response.text})"
                f" after ({request.method})"
                f" request to ({request.path_qs})"
            )
        else:
            Logger.log_error(
                f"Error Code ({response.status})"
                f" returned with text ({response.text})"
                f" after ({request.method})"
                f" request to ({request.path_qs})"
            )

    except Exception as exc:
        Logger.log_exception(
            "Unexpected exeption caught in router",
            exc
        )
        response = web.json_response(
            status=500,
            data={"error": "Exception in router"}
        )

    return response
