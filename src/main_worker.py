import os
from fastapi import FastAPI
from dtos import Task
from worker import Worker
import configuration
import threading
import logging
import my_utils

manager_ip_1 = os.getenv('MANAGER_NODE_IP_1')
if manager_ip_1 is None:
    logging.error("Dont have other manager ip 1!")
    raise NotImplementedError("Dont have other manager ip 1!")

manager_ip_2 = os.getenv('MANAGER_NODE_IP_2')
if manager_ip_2 is None:
    logging.error("Dont have other manager ip 2!")
    raise NotImplementedError("Dont have other manager ip 2!")

worker = Worker(manager_ip_1, manager_ip_2)

check_worker_is_idle = threading.Thread(target=worker.check_if_idle)

app = FastAPI()

@app.post(f"/{configuration.start_new_work_endpoint}")
def ask_to_start_working_on_new_work(task: Task) -> bool:
    busy = worker.busy # checking if busy
    if busy is True: # i am working
        return False # i cant work
    # start working
    busy = True
    worker.start_new_work(task) # on a different thread
    return True # i can work
    
