import base64
from fastapi import Body, FastAPI, Query, Request
import uuid
import logging
import my_utils
import json
import time
import consts
from spawn_worker import *
import threading
from dtos import Task, TaskResult

app = FastAPI()
def run_spawn_worker():
    logging.info(f"spawn_worker started!!")
    thread1 = threading.Thread(target=spawn_new_workers)
    thread1.start()
#    thread1.join()

@app.on_event("startup")
async def startup_event():
    run_spawn_worker()


@app.put("/enqueue")
def enqueue(iterations: int = Query(..., description="number of iterations", gt=0), buffer: bytes = Body(...)) -> str:
    logging.info(f'inside enqueue endpoint.')
    work_id = str(uuid.uuid4())
    new_task = Task(work_id, base64.b64encode(buffer).decode('utf-8'), iterations, timestamp=time.time())
    json_str = json.dumps(new_task.__dict__)
    logging.info(f'recieved new task\n{json_str}')
    my_utils.my_redis.rpush(consts.TASK_LIST, json_str)
    logging.info(f'set task in redis')
    return work_id

@app.post("/pullCompleted")
def pullCompleted(top: int = Query(..., description="number of getting the completed tasks", gt=0)):
    logging.info(f"inside pull completed top is {top}")
    num_of_elements = my_utils.my_redis.llen(consts.RESULT_LIST)
    if num_of_elements == 0:
        return "none"
    logging.info(f"length of {consts.RESULT_LIST} is {num_of_elements}")
    min_of_elements = min([num_of_elements,top])
    logging.info(f"inside pull min_of_elements is {min_of_elements}")
    elements =  my_utils.my_redis.lrange(consts.RESULT_LIST, 0, min_of_elements - 1)
    my_utils.my_redis.ltrim(consts.RESULT_LIST, min_of_elements, -1) 
    logging.info(f"inside pull completed endpoint got {len(elements)} elemnts")
    all_str = []
    if elements is None:
        return "none"
    for element in elements:
        stored_obj = json.loads(element)
        retrieved_obj = TaskResult(stored_obj['id'], stored_obj['output'])
        result_str = json.dumps(retrieved_obj.__dict__)
        logging.info(f"got this element {result_str}")
        all_str.append(retrieved_obj)
    return all_str

