#!/bin/bash

set -o errexit
set -o nounset

ruff check --fix .
ruff format .
