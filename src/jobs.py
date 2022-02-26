#! /usr/bin/env python3
"""
Handle all requests to the endpoints under /jobs/
"""

# default modules
import re
import json

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


async def run_job(job: str, mode: str) -> web.Response:
    """
    Run the specified job
    Returns a response based on the result
    """
    if not JOB_INPUT_REGEX.match(job):
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

    if mode == "verbatim":
        runtime_result = RUNTIME_INSTANCE.execute(job)
    elif mode == "simulation":
        runtime_result = RUNTIME_INSTANCE.simulate(job)
    elif mode == "echo":
        runtime_result = RUNTIME_INSTANCE.echo(job)
    else:
        Logger.log_error("Invalid job mode selected string")
        return web.json_response(
            status=400,
            data={
                "error": "Invalid Job Mode",
                "expected": "verbatim, simulation, or echo",
            }
        )

    if runtime_result != 0:
        runtime_error = Runtime.decode_error(runtime_result)
        return web.json_response(
            status=201,
            data={
                "runtime_error_code": runtime_result,
                "runtime_error_string": runtime_error,
                "mode": mode,
                "job": job,
            }
        )

    return web.json_response(
        status=201,
        data={
            "status": "job completed successfully",
            "mode": mode,
            "job": job,
        }
    )


async def add_job(request: web.Request) -> web.Response:
    """
    Adds a job to the runtime if the request is valid
    Returns the response that should be returned to the client
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

    try:
        request_json = json.loads(request_body)
    except json.decoder.JSONDecodeError:
        Logger.log_error(
            "User tried to add a job with a malformed request body"
            f" @ {request.path_qs}."
            f" Request body: {request_body}"
        )
        return web.json_response(
            status=400,
            data={
                "error": "Request body malformed",
                "expected": "application/json",
                "body": request_body
            }
        )

    job_input_str = request_json.get("job", "").upper()

    job_mode = request_json.get("mode", "").lower()

    return await run_job(job_input_str, job_mode)


ROOT_REGEX = re.compile(r"^\/jobs(\/|\?)$")
ADD_REGEX = re.compile(r"^\/jobs/add(\/|\?|$)")


async def router(request: web.Request) -> web.Response:
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
