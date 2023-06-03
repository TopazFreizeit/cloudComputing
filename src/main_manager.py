import logging
import os
from fastapi import Body, FastAPI, Query, Request
import uuid
from pydantic import BaseModel
import requests
import threading
from manager import Manager, workerInsideManager
import configuration
from task_result import TaskResult
import custom_logger

other_manager_ip = os.getenv('OTHER_MANAGER_IP')
if other_manager_ip is None:
    logging.error("Dont have other manager ip!")
    raise NotImplementedError("Dont have other manager ip!")

response = requests.get('https://api.ipify.org?format=json')
my_ip = response.json()['ip']

app = FastAPI()

manager = Manager(other_manager_ip=other_manager_ip, my_ip=my_ip)
manager_main_flow= threading.Thread(target=manager.start_main_flow)

@app.put("/enqueue")
def enqueue(iterations: int = Query(..., description="number of iterations", gt=0), buffer: bytes = Body(...)) -> str:
    work_id = str(uuid.uuid4())
    new_task = (work_id, buffer, iterations)
    logging.info(f'inside enqueue endpoint recieved new task {new_task}')
    manager.add_task(new_task)
    return work_id

@app.post("/pullCompleted")
async def exit(top: str = Query(..., description="number of getting the completed tasks")):
    return manager.get_task_results()[:top]


# add worker endpoint
@app.post(f"/{configuration.add_worker_endpoint}")
def process_data(new_worker: workerInsideManager):
    logging.info(f'the second manager have told me he created a new worker with ip {new_worker.ip}')
    manager.add_worker(new_worker)

# complete task endpoint
@app.post(f"/{configuration.complete_task_endpoint}")
def complete_work(task_result: TaskResult):
    logging.info(f'a worker node just told me he finished task id {task_result.id}')
    manager.add_task_result(task_result)

@app.get(f"/{configuration.remove_worker_endpoint}")
def remove_worker(request: Request):
    logging.info(f'inside remove worker endpoint')
    if request.client:
        worker_ip = request.client.host
        logging.info(f'the worker node ip is {worker_ip} and now i need to remove it')
        manager.remove_worker_node(worker_ip)
    else:
        logging.error(f'could not get the ip from the request of the worker node')
