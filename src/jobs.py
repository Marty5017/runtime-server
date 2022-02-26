#! /usr/bin/env python3
"""
Handle all requests to the endpoints under /jobs/
"""

# pylint: disable=broad-except

# disable the too-many returns warning because the many returns make sense here
# pylint: disable=too-many-return-statements

# default modules
import re
import json
import time
import threading

# installed modules
from aiohttp import web

# custom modules
import logger as Logger
from runtime import Runtime
from storage import STORAGE_INSTANCE

# pylint: disable=fixme
# TODO: this key must be moved to an environment variable
API_KEY = '$YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V='

JOB_INPUT_REGEX = re.compile(r"^[XYZ]\(\d{1,3}\)(, [XYZ]\(\d{1,3}\))*$")

RUNTIME_INSTANCES = []
for i in range(0, 5):
    RUNTIME_INSTANCES.append(Runtime(i + 1))


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

    if mode not in ["verbatim", "simulation", "echo"]:
        Logger.log_error("Invalid job mode selected string")
        return web.json_response(
            status=400,
            data={
                "error": "Invalid Job Mode",
                "expected": "verbatim, simulation, or echo",
            }
        )

    job_id = STORAGE_INSTANCE.add_job(job, mode)

    job_thread = threading.Thread(
        target=job_thread_handler,
        daemon=False,
        args=(job_id, job, mode)
    )
    job_thread.start()

    return web.json_response(
        status=201,
        data={
            "id": job_id,
            "mode": mode,
            "job": job,
        }
    )


def job_thread_handler(job_id: int, job: str, mode: str):
    """
    This method is intended to run in its own thread.
    This method starts the job on the runtime, waits for it to complete,
    then updates the status of the job in storage
    """

    is_started = False
    runtime_id = None

    # loop until the job has been started
    while not is_started:
        # search for a runtime that is available
        for instance in RUNTIME_INSTANCES:
            runtime_id = instance.runtime_id
            if instance.get_is_available():
                STORAGE_INSTANCE.update_job(
                    job_id,
                    "Started",
                    runtime_id
                )
                if mode == "verbatim":
                    runtime_result = instance.execute(job)
                elif mode == "simulation":
                    runtime_result = instance.simulate(job)
                elif mode == "echo":
                    runtime_result = instance.echo(job)
                if runtime_result < 0:
                    STORAGE_INSTANCE.update_job(
                        job_id,
                        "Retrying"
                    )
                else:
                    is_started = True
                    break

        # if none of the runtimes are available just sleep before trying again
        if not is_started:
            time.sleep(1)

    status = "Success" if runtime_result == 0 else "Runtime Error"

    STORAGE_INSTANCE.update_job(
        job_id,
        status,
        runtime_id,
        runtime_result,
        None if runtime_result == 0 else Runtime.decode_error(runtime_result)
    )


async def view_job(request: web.Request, job_id: int) -> web.Response:
    """
    Retrieves all of the info for the specified job from storage
    """
    if request.method != "GET":
        Logger.log_error(
            f"User tried to {request.method} to {request.path_qs}. Only POST requests are allowed"
        )
        return web.json_response(
            status=400,
            data={
                "error":
                "Only GET requests are allowed on this route"
            }
        )

    job_data = STORAGE_INSTANCE.get_job(job_id)

    return web.json_response(
        status=200,
        data=job_data
    )


async def list_jobs(request: web.Request) -> web.Response:
    """
    Retrieves all of the jobs from storage
    TODO: add pagination
    """
    if request.method != "GET":
        Logger.log_error(
            f"User tried to {request.method} to {request.path_qs}. Only POST requests are allowed"
        )
        return web.json_response(
            status=400,
            data={
                "error":
                "Only GET requests are allowed on this route"
            }
        )

    job_rows = STORAGE_INSTANCE.list_jobs()

    return web.json_response(
        status=200,
        data={
            "count": len(job_rows),
            "rows": job_rows
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
ADD_REGEX = re.compile(r"^\/jobs/add(\/$|\?|$)")
LIST_REGEX = re.compile(r"^\/jobs/list(\/$|\?|$)")
VIEW_REGEX = re.compile(r"^\/jobs/(\d+)(\/$|\?|$)")


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
        if LIST_REGEX.match(request_path):
            return await list_jobs(request)
        view_match = VIEW_REGEX.match(request_path)
        if view_match:
            return await view_job(request, view_match.group(1))

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
