import os
from fastapi import Body, FastAPI, Query
import uuid

from pydantic import BaseModel
import requests

from manager import Manager
import configuration
from task_result import TaskResult

other_manager_ip = os.getenv('OTHER_MANAGER_IP')
if other_manager_ip is None:
    raise NotImplementedError("Dont have other manager ip!")

response = requests.get('https://api.ipify.org?format=json')
my_ip = response.json()['ip']

app = FastAPI()

manager = Manager(other_manager_ip=other_manager_ip, my_ip=my_ip)

@app.put("/enqueue")
def enqueue(iterations: int = Query(..., description="number of iterations", gt=0), buffer: bytes = Body(...)) -> str:
    work_id = str(uuid.uuid4())
    new_task = (work_id, buffer, iterations)
    manager.add_task(new_task)
    # TODO adding scaling mechanism
    return work_id

@app.post("/pullCompleted")
async def exit(top: str = Query(..., description="number of getting the completed tasks")):
    return manager.get_task_results()[:top]


class WorkerStatusModel(BaseModel):
    worker_ip: str

# add worker endpoint
@app.post(f"/{configuration.add_worker_endpoint}")
def process_data(request_data: WorkerStatusModel):
    worker_ip = request_data.worker_ip
    manager.add_worker(worker_ip)

# complete task endpoint
@app.post(f"/{configuration.complete_task_endpoint}")
def complete_work(task_result: TaskResult):
    manager.add_task_result(task_result)
    
