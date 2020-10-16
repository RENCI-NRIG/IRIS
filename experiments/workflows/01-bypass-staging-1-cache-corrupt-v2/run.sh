#!/bin/bash
set -e
./../../common/reset_caches.py uc-cache
./iris-experiment-driver.py uc-cache uc test_log_file -m 9 &
./workflow.py uc /home/tanaka/test3 run9 10 --populate --timestamps-file ts_file
