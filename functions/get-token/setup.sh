#!/bin/bash
# you need to run this before deploying because the dependencies are in .gitignore
cd $(dirname "$0")
pip install -r requirements.txt -t modules/
