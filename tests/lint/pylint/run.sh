#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: run.sh <target>"
    exit 1
fi

readonly SCRIPT_DIR=$(cd $(dirname $0); pwd)
readonly PYTHON_SCRIPT_DIRECTORY=${1}
readonly PYLINT_CMD="pylint"

# pylint
error=0
for file in `find ${PYTHON_SCRIPT_DIRECTORY} -name "*.py" | sort`; do
    echo "======= pylint "${file}" ======="

    ${PYLINT_CMD} ${file}
    ret=`echo $?`
    if [ $? -ne 0 ]; then
        ((error+=1))
    fi
done

if ((error > 0)); then
    echo "Error: ${error} files have errors."
    exit 1
fi

exit 0
