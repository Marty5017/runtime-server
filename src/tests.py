#!/usr/bin/env python3

"""
This module includes all unit tests
"""

# installed modules
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

# custom modules
import router as Router
from runtime import Runtime


# pylint: disable=fixme
# TODO: this key must be moved to an environment variable
TEST_HEADERS = {
    "api_key": '$YboMhcaz7U+3;;M(~t|BX-~ 2kw|ZII2e+s$pw5sBqf$?g]-BYlq.! R/qMR/V='
}


class RestRequestTestCase(AioHTTPTestCase):
    """
    This test case handles all REST requests.
    This test case can possibly be split into a separate case for each api
    function, but it is fine for now
    """
    async def get_application(self):
        """
        Override the base class function to set up our server app
        """
        app = web.Application()
        app.add_routes([web.route('*', r'/{tail:.*}', Router.entry_point)])
        return app

    async def test_options(self):
        """
        Test the OPTIONS request
        """
        async with self.client.options("/") as resp:
            self.assertEqual(resp.status, 200)
            self.assertEqual(
                resp.headers.get("Access-Control-Allow-Origin"),
                "*"
            )
            self.assertEqual(
                resp.headers.get("Access-Control-Allow-Methods"),
                "*"
            )
            self.assertEqual(
                resp.headers.get(
                    "Access-Control-Allow-Headers"
                ),
                ('Content-Type,'
                 ' api_key,'
                 ' Content-Length,'
                 ' X-Requested-With,'
                 ' x-reset-id,'
                 ' x-reset-token')
            )

    async def test_404(self):
        """
        Test a known undefined path
        """
        async with self.client.get("/what/is/this/") as resp:
            self.assertEqual(resp.status, 404)
            data = await resp.json()
            self.assertEqual(
                data,
                {"error": "Not Found"}
            )

    async def test_jobs_no_auth(self):
        """
        Test a request to the jobs endpoint without authentication
        """
        async with self.client.post("/jobs/") as resp:
            self.assertEqual(resp.status, 401)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error": "api_key header cannot be empty"
                }
            )

    async def test_jobs_invalid_auth(self):
        """
        Test a request to the jobs endpoint without an invalid
        authentication key
        """
        async with self.client.post(
            "/jobs/",
            headers={"api_key": "invalid"}
        ) as resp:
            self.assertEqual(resp.status, 403)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error": "Invalid api_key header"
                }
            )

    async def test_jobs_root(self):
        """
        Test a request to the root /jobs/ endpoint
        """
        async with self.client.get(
            "/jobs/",
            headers=TEST_HEADERS
        ) as resp:
            self.assertEqual(resp.status, 400)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error": "Please select a function under the jobs endpoint"
                }
            )

    async def test_jobs_undefined_function(self):
        """
        Test a request to a function under /jobs/ that does not exist
        """
        async with self.client.post(
            "/jobs/invalid",
            headers=TEST_HEADERS
        ) as resp:
            self.assertEqual(resp.status, 404)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error": "Not Found",
                    "note": "This function is not defined",
                }
            )

    async def test_jobs_add_get(self):
        """
        Test a GET request to /jobs/add/
        """
        async with self.client.get(
            "/jobs/add/",
            headers=TEST_HEADERS
        ) as resp:
            self.assertEqual(resp.status, 400)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error":
                    "Only POST requests are allowed on this route"
                }
            )

    async def test_jobs_add_no_body(self):
        """
        Test a request to /jobs/add/ without a body
        """
        async with self.client.post(
            "/jobs/add/",
            headers=TEST_HEADERS
        ) as resp:
            self.assertEqual(resp.status, 400)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "error":
                    "This route requires a body"
                }
            )

    async def test_jobs_add_invalid_payload(self):
        """
        Test a series of requests to /jobs/add/ with invalid bodies
        """
        test_inputs = [
            "aX(0), Y(0), X(0)",
            "X(0), Y(0), X(0)b",
            "X(0), cY(0), X(0)",
            "X(0",
            ", X(0)",
        ]
        for test in test_inputs:
            async with self.client.post(
                "/jobs/add/",
                headers=TEST_HEADERS,
                data=test
            ) as resp:
                self.assertEqual(resp.status, 400)
                text = await resp.text()
                self.assertIn("Job string not in the valid format", text)

    async def test_jobs_add_runtime_errors(self):
        """
        Test a series of requests to /jobs/add/ with valid bodies that return
        runtime errors
        """
        test_inputs = [
            ("X(90), Y(0), Z(90)", 1),
            ("Z(0), Z(180), X(90)", 2),
            ("Z(90), Y(180), X(0)", 3),
            ("X(90), Y(180), X(90)", 4),
            ("X(180), Y(180), X(180)", 4),
            ("X(0), Y(0)", 4),
            ("X(0)", 4),
        ]
        for test in test_inputs:
            test_error_str = Runtime.decode_error(test[1])
            async with self.client.post(
                "/jobs/add/",
                headers=TEST_HEADERS,
                data=test[0]
            ) as resp:
                self.assertEqual(resp.status, 201)
                data = await resp.json()
                self.assertEqual(
                    data,
                    {
                        "runtime_error_code": test[1],
                        "runtime_error_string": test_error_str
                    }
                )

    async def test_jobs_add_runtime_success(self):
        """
        Test a request to /jobs/add/ that returns runtime success
        """
        async with self.client.post(
            "/jobs/add/",
            headers=TEST_HEADERS,
            data="X(0), Y(0), X(0)"
        ) as resp:
            self.assertEqual(resp.status, 201)
            data = await resp.json()
            self.assertEqual(
                data,
                {
                    "status": "job completed successfully"
                }
            )
