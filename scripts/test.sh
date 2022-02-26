#! /usr/bin/env bash

# remove old logs
rm logs/all.log 2> /dev/null || true
rm logs/error.log 2> /dev/null || true
rm logs/exception.log 2> /dev/null || true


cd src
rm jobs.db 2> /dev/null || true
python3 -m unittest