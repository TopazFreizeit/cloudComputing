import base64
import json
from pydantic import BaseModel
import logging
import requests
from task import Task
import boto3
import configuration
from task_result import TaskResult
from typing import Union
import time
from queue import Queue

class workerInsideManager(BaseModel):
    def __init__(self, ip:str, instance_id:str):
        self.ip=ip
        self.instance_id=instance_id

class Manager:
    def __init__(self, other_manager_ip:str, my_ip:str):
        self.tasks : Queue[Task] = Queue()
        self.workers : list[workerInsideManager] = []
        self.task_results: list[TaskResult] = []
        self.other_manager_ip: str = other_manager_ip
        self.my_ip = my_ip
        # Initialize the AWS EC2 client
        self.ec2_client: boto3.resource.fac = boto3.client('ec2', region_name=configuration.region_name)

    def add_task(self, task):
        self.tasks.put(task)

    def get_tasks(self):
        return self.tasks

    def add_worker(self, worker: workerInsideManager):
        self.workers.append(worker)

    def remove_worker(self, worker):
        del self.workers[worker]

    def get_workers(self):
        return self.workers


    def add_task_result(self, result):
        self.task_results.append(result)

    def get_task_results(self):
        return self.task_results
    
    
    def ask_worker_node_to_process_new_task(self, worker: workerInsideManager, task:Task) -> Union[workerInsideManager,None]:
        logging.info(f'checking with worker {worker.ip} if it can get a new task, and sending him the task at the same time {task.id}')
        new_worker = None
        url = f'http://{worker.ip}/{configuration.start_new_work_endpoint}'
        json_payload = json.dumps(task.__dict__)
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url=url, data=json_payload, headers=headers)
        logging.info(f'worker node with ip {worker.ip} answerd with code {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            if data is True:
                new_worker = worker
        return new_worker 
    
    def create_new_worker_node(self)->workerInsideManager:
        env_vars: dict[str,str]
        # Specify the user data script
        user_data = f'''
            #!/bin/bash
            yum update -y
            yum install -y git
            yum install -y python3
            yum install -y python3-pip
            pip3 install "uvicorn[standard]" fastapi boto3
            git clone https://github.com/TopazFreizeit/cloudComputing.git
            cd cloudComputing
            cd src
            export MANAGER_NODE_IP_1={self.my_ip}
            export MANAGER_NODE_IP_2={self.other_manager_ip}
            uvicorn main_worker:app --host 0.0.0.0 --port 80
        '''
        response = self.ec2_client.create_instances(
            ImageId=configuration.ami_id,
            InstanceType=configuration.instance_type,
            SecurityGroups=[configuration.security_group_id],
            MinCount=1,
            MaxCount=1,
            UserData=user_data
        )
        instance = response[0]
        instance.wait_until_running() # Wait until the instance reaches the "running" state
        instance.load() # Refresh the instance object to get the latest information
        instance_id:str = instance.id # Retrieve the instance ID and public IP address
        public_ip:str = instance.public_ip_address
        new_worker = workerInsideManager(instance_id=instance_id, ip=public_ip)
        self.add_worker(new_worker)
        return new_worker
    
    def remove_worker_node(self, worker_ip:str):
        logging.info(f'want to remove worker with ip {worker_ip} need to find its instance_id, now i loop thorugh all my known worker nodes')
        ec2_client = boto3.client('ec2')
        instance_id = None
        worker_to_be_removed = None
        for worker in self.workers:
            logging.info(f'the ip of the current worker node is {worker.ip}')
            if worker.ip == worker_ip:
                logging.info(f'found the instance id and it is {worker.instance_id}')
                instance_id=worker.instance_id
                worker_to_be_removed=worker
        if instance_id is not None:
            logging.info(f'going to terminate worker with id {instance_id}')
            response = ec2_client.terminate_instances(InstanceIds=[instance_id])
            if response['TerminatingInstances'][0]['CurrentState']['Name'] == 'shutting-down':
                logging.info(f"Worker instance {instance_id} terminated successfully.")
            else:
                logging.error(f"Failed to terminate worker instance {instance_id} it response is {response}.")
        else:
            logging.error(f"did not found a worker node with ip {worker_ip}!!!")
        if worker_to_be_removed is not None:
            logging.info(f'after terminating need to remove the worker from my list')
            self.workers.remove(worker_to_be_removed)
    
    
    def find_worker_node(self, task : Task)->Union[workerInsideManager, None]:
        worker:Union[workerInsideManager, None] = None
        while worker is None:
            for worker in self.workers:
                    worker = self.ask_worker_node_to_process_new_task(worker, task)
                    if worker is not None:
                        break
            if worker is None and len(self.workers) < 5:
                new_worker = self.create_new_worker_node()
                worker = self.ask_worker_node_to_process_new_task(new_worker, task)
                json_payload = json.dumps(new_worker.__dict__)
                headers = {
                    "Content-Type": "application/json"
                }
                url = f'http://{self.other_manager_ip}/{configuration.add_worker_endpoint}'
                logging.info(f'just created a new worker with ip {worker.ip if worker else None} so need to upadte the other manager with url {url}')
                response = requests.post(url=url, data= json_payload, headers=headers)
                logging.info(f'the other manager responded with status code {response.status_code}')
        return worker
    
    def start_main_flow(self):
        while True:
            time.sleep(5)
            if not self.tasks.empty():
                task = self.tasks.get()
                self.find_worker_node(task=task)