#!/usr/bin/bash
autoflake -r --remove-unused-variables --remove-all-unused-imports --in-place .
autopep8 . -r --in-place --experimental --aggressive --max-line-length 120
isort -rc .
