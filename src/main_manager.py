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
import my_utils
import time
import boto3
app = FastAPI()

my_num = os.getenv('MY_NUM')
# Specify the instance name you want to get the IP address for
if(my_num ==1):
    instance_name = 'InfraStack/ec2-instance-2'
else:
    instance_name = 'InfraStack/ec2-instance-1'

# Retrieve all instances
client = boto3.client('ec2','us-east-1')
response = client.describe_instances()
other_manager_ip = ""
# Iterate over reservations and instances to find the matching instance
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        # Check if the instance has a Name tag and it matches the specified instance name
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name' and tag['Value'] == instance_name:
                    # Retrieve the IP address of the matching instance
                    other_manager_ip = instance['PublicIpAddress'].split()[2]
                    logging.info(f"IP address of other manager:{other_manager_ip}")
                    break
response = requests.get('https://api.ipify.org?format=json')
my_ip = response.json()['ip']
#other_manager_ip = os.getenv('OTHER_MANAGER_IP')

logging.info(f"manager node just started with my ip of {my_ip} and other managaer ip of {other_manager_ip}")

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