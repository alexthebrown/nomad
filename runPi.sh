#!/bin/bash

cd nomad/nomad
source .venv/bin/activate

sudo --preserve-env=VIRTUAL_ENV,PATH python piStartScript.py
