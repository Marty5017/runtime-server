# OQC Technical Test

## Description

This system hosts a server that receives jobs, runs them on an externally
sourced runtime, and returns the response from the runtime

## Installation

To install all required modules, please run

    pip install -r requirements.txt

## Usage

These instructions are for an Ubnuntu Linux system, but should work on any
posix system

run all tests and linting (testing takes about a minute to complete):

    ./scripts/run_tests_and_linting.sh

run all tests (testing takes about a minute to complete):

    ./scripts/test.sh

run linting:

    ./scripts/lint.sh

start the server by running the start_server script from the root directory:

    ./scripts/start_server.sh

## API

All endpoints currently just require the API key in the header to be authorised

API header:

    {
        "api_key": '$YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V='
    }

### Add Job

endpoint: /jobs/add/
request method: POST

This endpoint allows you to load a new job. The endpoint will return immediatly
with the id of the job, which can then be used to query the status of the job

body format example:

    {
      "job": "X(90), Y(180), X(90)",
      "mode": "verbatim",
    }

job field format: "{Axis}({Angle}}, {Axis}({Angle}), ..."
job field regex: `r"^[XYZ]\(\d{1,3}\)(, [XYZ]\(\d{1,3}\))*$"`

example jobs:

    "X(90), Y(180), X(90)"
    "X(0)"
    "Z(180), Y(180)"

mode field format: "{mode}"
mode field options: "verbatim", "simulation", or "echo"

modes:

1. verbatim: Invoke the runtime
2. simulation: a simulator is used instead of the full hardware connected runtime
3. echo: the system fakes return codes from the runtime without doing anything else

example request:

    curl --location --request POST 'http://localhost:12021/jobs/add/' \
    --header 'api_key: $YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V=' \
    --header 'Content-Type: text/plain' \
    --data-raw '{
      "job": "X(0), Y(0), X(0)",
      "mode": "verbatim"
    }'

### List Jobs

endpoint: /jobs/list/
request method: GET

This endpoint allows you to retrieve a list of all of the jobs on the system.
TODO: update this endpoint to allow for pagination

example request:

    curl --location --request GET 'http://localhost:12021/jobs/list/' \
    --header 'api_key: $YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V=' \
    --header 'Content-Type: text/plain'

### Get Job

endpoint: /jobs/{id}/
request method: GET

This endpoint allows you to retrieve the details of a specific job by id where
id is an integer.
On error a 0 is returned

object fields:

    id: job's id in the database
    job: string used to start the job
    mode: selected mode for this job ("verbatim", "simulation", or "echo")
    status: status of the job. Starts at "Starting", can go to "Retrying", ends in either "Success" or "Runtime Error",
    runtime: id of the runtime that was used for this job. It is None untill the job has started
    return_code: None untill started, then 0 on success and >0 on error
    runtime_error: string to describe the runtime error
    created_time: UTC time when the job was added to the system
    start_time: UTC time when the job was started on a runtime
    end_time: UTC time when the job was completed by a runtime

example request:

    curl --location --request GET 'http://localhost:12021/jobs/list/' \
    --header 'api_key: $YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V=' \
    --header 'Content-Type: text/plain'
