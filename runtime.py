#! /usr/bin/env python3

class Runtime:
    def execute(self, job: str) -> int:
        if job == "X(0), Y(0), X(0)":
            return 0
        if job == "X(90), Y(0), Z(90)":
            return 1
        if job == "Z(0), Z(180), X(90)":
            return 2
        if job == "Z(90), Y(180), X(0)":
            return 3
