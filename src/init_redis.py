import redis
import my_utils
import logging
from consts import LOCK
import time


my_redis = redis.Redis(host='localhost', port=6379, db=0)

logging.info("have connection with Redis and set the lock")
## wait for redis connection
ok = False
while not ok:
    try:
        my_redis.set(LOCK,"locked")
        ok = True
    except Exception:
        logging.warn("do not have connection with Redis waiting")
        time.sleep(10)