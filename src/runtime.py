#! /usr/bin/env python3
"""
This module houses the runtime functionality.
The content of this module can be replaced by any other implementation as long
as the interface remains constant
"""


# pylint: disable=no-self-use
class Runtime:
    """
    This class will hold all properties of the runtime interface
    """

    ERROR_LOOKUP = {
        1: "Error Code 1 TBD",
        2: "Error Code 2 TBD",
        3: "Error Code 3 TBD",
    }

    def execute(self, job: str) -> int:
        """
        Executes a job with the runtime
        Just return the output from echo for debugging
        """
        return self.echo(job)

    def simulate(self, job: str) -> int:
        """
        Simulates a job on a simulation of the runtime interface
        Just return the output from echo for debugging
        """
        return self.echo(job)

    def echo(self, job: str) -> int:
        """
        Return fake retun codes
        Hard coded for debugging
        """
        if job == "X(0), Y(0), X(0)":
            return 0
        if job == "X(90), Y(0), Z(90)":
            return 1
        if job == "Z(0), Z(180), X(90)":
            return 2
        if job == "Z(90), Y(180), X(0)":
            return 3
        return 4

    @staticmethod
    def decode_error(error: int) -> str:
        """
        This function just converts the integer error codes returned by execute
        to human readable strings
        """
        return Runtime.ERROR_LOOKUP.get(error, "Unknown Error")
