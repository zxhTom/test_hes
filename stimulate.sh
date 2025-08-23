#!/bin/bash
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE:-$0}")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
cd $SCRIPT_DIR
echo "Env..."
echo $TEST_ENV
echo $TEST_REPORT_ENABLED
echo "Env..."
echo $PATH
python -m pytest --alluredir=./allure-results -s --count=1 -v
