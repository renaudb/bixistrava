#!/bin/bash

# Simple script to format and typecheck code.

./.venv/bin/mypy \
     bixistrava/ \
     test/

./.venv/bin/yapf -i -r \
     bixistrava/ \
     test/
