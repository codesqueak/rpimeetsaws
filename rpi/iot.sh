#!/bin/bash
#
# restart loop until process terminates with state 0
# this is used to stop in a controlled manner, ctrl-c into the python process
#
until python3 newsend.py; do
    echo "IoT watchdog timeout - restart." >&2
    sleep 1
done
