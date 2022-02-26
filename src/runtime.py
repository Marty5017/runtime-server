#! /usr/bin/env python3
"""
This module houses the runtime functionality.
The content of this module can be replaced by any other implementation as long
as the interface remains constant
"""

import time
import threading

# pylint: disable=no-self-use
# pylint: disable=fixme
# pylint: disable=consider-using-with


class Runtime:
    """
    This class will hold all properties of the runtime interface
    """

    ERROR_LOOKUP = {
        1: "Error Code 1 TBD",
        2: "Error Code 2 TBD",
        3: "Error Code 3 TBD",
    }

    def __init__(self, runtime_id: int) -> None:
        self.runtime_id = runtime_id
        self.is_available = False
        self.lock = threading.Lock()

        # self.is_startup is just for testing now. To verify that the system is
        # looping through all runtimes and then waits before trying again
        # TODO: remove
        self.is_startup = True

    def execute(self, job: str) -> int:
        """
        Executes a job with the runtime
        Just return the output from echo for debugging

        Return: -1 on failed to start
                 0 on success
                >0 on runtime error
        """
        return self.echo(job)

    def simulate(self, job: str) -> int:
        """
        Simulates a job on a simulation of the runtime interface
        Just return the output from echo for debugging

        Return: -1 on failed to start
                 0 on success
                >0 on runtime error
        """
        return self.echo(job)

    def echo(self, job: str) -> int:
        """
        Return fake retun codes
        Hard coded for debugging

        Return: -1 on failed to start
                 0 on success
                >0 on runtime error
        """
        self.lock.acquire()
        start_is_available = self.is_available
        self.lock.release()

        if not start_is_available:
            return -1

        self.lock.acquire()
        self.is_available = False
        self.lock.release()

        job_return_code = 4

        time.sleep(1)
        if job == "X(0), Y(0), X(0)":
            job_return_code = 0
        if job == "X(90), Y(0), Z(90)":
            job_return_code = 1
        if job == "Z(0), Z(180), X(90)":
            job_return_code = 2
        if job == "Z(90), Y(180), X(0)":
            job_return_code = 3

        self.lock.acquire()
        self.is_available = True
        self.lock.release()

        return job_return_code

    def get_is_available(self) -> bool:
        """
        Thread safe way to test if this runtime is available
        """
        self.lock.acquire()
        retval = self.is_available

        # self.is_startup is just for testing now. To verify that the system is
        # looping through all runtimes and then waits before trying again
        # TODO: remove
        if self.is_startup:
            self.is_available = True
            self.is_startup = False
        self.lock.release()
        return retval

    @staticmethod
    def decode_error(error: int) -> str:
        """
        This function just converts the integer error codes returned by execute
        to human readable strings
        """
        return Runtime.ERROR_LOOKUP.get(error, "Unknown Error")
