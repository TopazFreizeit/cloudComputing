import json
import threading
import my_utils
import consts
import logging
from dtos import Task
import time


def check_if_more_than_15sec_from_last_task():
    elements = my_utils.my_redis.lrange(consts.TASK_LIST,0,0)
    logging.info(f"inside check_of_much_time_from_last_task got {len(elements)} elemnts")
    for element in elements:
        stored_obj = json.loads(element)
        task = Task(stored_obj['id'], stored_obj['buffer'], int(stored_obj['iterations']), float(stored_obj['timestamp']))
        result_str = json.dumps(task.__dict__)
        logging.info(f"got this element {result_str} on top of the task list")
        time_elapsed = time.time() - task.timestamp
        logging.info(f"time_elapsed {time_elapsed}")
        if time_elapsed > 15:
            return True
    return False


def acquire_lock(lock_key):
    acquired = my_utils.my_redis.set(lock_key, 'locked', nx=True)
    return acquired

def release_lock(lock_key):
    my_utils.my_redis.delete(lock_key)
    
def spawn_new_workers():
    while True:
        time.sleep(5)
        more_than_15_sec = check_if_more_than_15sec_from_last_task()
        num_of_workers = my_utils.my_redis.get(consts.NUM_OF_WORKERS)
        logging.info(f"num_of_workers {num_of_workers}")
        if not num_of_workers:
            num_of_workers = 0
        num_of_workers = int(num_of_workers)
        if more_than_15_sec and acquire_lock(consts.LOCK) and num_of_workers < 5:
            my_utils.create_new_ec2_instance_worker()
            my_utils.my_redis.set(consts.NUM_OF_WORKERS, str(num_of_workers + 1))
        release_lock(consts.LOCK)

# if __name__ == "__main__":
#     logging.info(f"spawn_worker started!!")
#     thread1 = threading.Thread(target=spawn_new_workers)
#     thread1.start()
#     thread1.join()

# def run_spawn_worker():
#     logging.info(f"spawn_worker started!!")
#     thread1 = threading.Thread(target=spawn_new_workers)
#     thread1.start()
#     thread1.join()