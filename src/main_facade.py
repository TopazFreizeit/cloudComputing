import base64
from fastapi import Body, FastAPI, Query, Request
import uuid
import logging
import my_utils
import json
import time

from dtos import Task, TaskResult


app = FastAPI()

# TODO
# in a different thread make the up scaling happen
# create a new lock for the spawn of a new worker
# if lock do not exist (my_utils.my_redis.get("lock")) create new string named lock and make it value to 1 
# my_utils.my_redis.set("lock","1")


@app.put("/enqueue")
def enqueue(iterations: int = Query(..., description="number of iterations", gt=0), buffer: bytes = Body(...)) -> str:
    logging.info(f'inside enqueue endpoint.')
    work_id = str(uuid.uuid4())
    new_task = Task(work_id, base64.b64encode(buffer).decode('utf-8'), iterations, timestamp=time.time())
    json_str = json.dumps(new_task.__dict__)
    logging.info(f'recieved new task\n{json_str}')
    my_utils.my_redis.lpush('new-tasks-list', json_str)
    logging.info(f'set task in redis')
    return work_id

@app.post("/pullCompleted")
async def exit(top: int = Query(..., description="number of getting the completed tasks", gt=1)):
    elements = my_utils.my_redis.lpop('result-tasks-list', top)
    logging.info(f"inside pull completed endpoint got {len(elements)} elemnts")
    all_str = []
    for element in elements:
        stored_obj = json.loads(element)
        retrieved_obj = TaskResult(stored_obj['id'], stored_obj['output'])
        result_str = json.dumps(retrieved_obj.__dict__)
        logging.info(f"got this element {result_str}")
        all_str.append(retrieved_obj)
    return all_str