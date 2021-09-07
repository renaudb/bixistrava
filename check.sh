#!/bin/bash

# Simple script to format and typecheck code.

./.venv/bin/mypy \
     *.py \
     bixi/*.py \
     strava/*.py

./.venv/bin/yapf -i \
     *.py \
     bixi/*.py \
     strava/*.py
