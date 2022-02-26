#! /usr/bin/env python3
"""
Handle all requests to the endpoints under /jobs/
"""

# default modules
import re

# installed modules
from aiohttp import web

# custom modules
import logger as Logger
from runtime import Runtime

# pylint: disable=fixme
# TODO: this key must be moved to an environment variable
API_KEY = '$YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V='

JOB_INPUT_REGEX = re.compile(r"^[XYZ]\(\d{1,3}\)(, [XYZ]\(\d{1,3}\))*$")

RUNTIME_INSTANCE = Runtime()


async def add_job(request):
    """
    Adds a job to the runtime if the request is valid
    """
    if request.method != "POST":
        Logger.log_error(
            f"User tried to {request.method} to {request.path_qs}. Only POST requests are allowed"
        )
        return web.json_response(
            status=400,
            data={
                "error":
                "Only POST requests are allowed on this route"
            }
        )

    if not request.body_exists:
        Logger.log_error(
            f"User tried to add an entry without a request body @ {request.path_qs}"
        )
        return web.json_response(
            status=400,
            data={
                "error":
                "This route requires a body"
            }
        )

    request_body = await request.text()

    if not JOB_INPUT_REGEX.match(request_body):
        Logger.log_error("Invalid job string")
        return web.json_response(
            status=400,
            data={
                "error": "Job string not in the valid format",
                "expected_format": "{Axis}({Angle}}, {Axis}({Angle}), ... ",
                "examples": [
                    "X(90), Y(180), X(90)",
                    "X(90)",
                ]
            }
        )

    runtime_result = RUNTIME_INSTANCE.execute(request_body)
    if runtime_result != 0:
        runtime_error = Runtime.decode_error(runtime_result)
        return web.json_response(
            status=201,
            data={
                "runtime_error_code": runtime_result,
                "runtime_error_string": runtime_error,
            }
        )

    return web.json_response(
        status=201,
        data={
            "status": "job completed successfully"
        }
    )

ROOT_REGEX = re.compile(r"^\/jobs(\/|\?)$")
ADD_REGEX = re.compile(r"^\/jobs/add(\/|\?|$)")


async def router(request):
    """
    Route the job request to the appropriate handler funcion
    """
    try:
        api_header = request.headers.get("api_key", None)
        if not api_header:
            return web.json_response(
                status=401,
                data={
                    "error": "api_key header cannot be empty"
                }
            )
        if api_header != API_KEY:
            return web.json_response(
                status=403,
                data={
                    "error": "Invalid api_key header"
                }
            )

        request_path = request.path

        if ROOT_REGEX.match(request_path):
            return web.json_response(
                status=400,
                data={
                    "error": "Please select a function under the jobs endpoint"
                }
            )

        if ADD_REGEX.match(request_path):
            return await add_job(request)

        return web.json_response(
            status=404,
            data={
                "error": "Not Found",
                "note": "This function is not defined",
            }
        )

    except Exception as exc:
        Logger.log_exception(
            "Exeption caught in jobs.router function",
            exc
        )
        raise
