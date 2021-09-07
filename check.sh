#!/bin/bash

# Simple script to format and typecheck code.

./.venv/bin/mypy \
     bixistrava/*.py \
     bixistrava/bixi/*.py \
     bixistrava/strava/*.py

./.venv/bin/yapf -i \
     bixistrava/*.py \
     bixistrava/bixi/*.py \
     bixistrava/strava/*.py
