import base64
import json
import requests
from main_manager import TaskResultModel, WorkerStatusModel
from task import Task
import boto3
import configuration
from task_result import TaskResult

class Manager:
    def __init__(self, other_manager_ip:str, my_ip:str):
        self.tasks : list[Task] = []
        self.workers : list[str] = []
        self.task_results: list[TaskResult] = []
        self.other_manager_ip: str = other_manager_ip
        self.my_ip = my_ip
        # Initialize the AWS EC2 client
        self.ec2_client: boto3.resource.fac = boto3.client('ec2', region_name=configuration.region_name)

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)

    def get_tasks(self):
        return self.tasks

    def add_worker(self, worker):
        self.workers.append(worker)

    def remove_worker(self, worker):
        del self.workers[worker]

    def get_workers(self):
        return self.workers


    def add_task_result(self, result):
        self.task_results.append(result)

    def get_task_results(self):
        return self.task_results
    
    
    
    def ask_worker_node_to_process_new_task(self, worker_ip):
        ip = None
        url = f'http://{worker_ip}/{configuration.start_new_work_endpoint}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data is True:
                ip = worker_ip
        return ip 
    
    def create_new_worker_node(self):
        env_vars: dict[str,str]
        # Specify the user data script
        user_data = f'''
            #!/bin/bash
            yum update -y
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
            MinCount=1,
            MaxCount=1,
            UserData=user_data
        )
        instance = response[0]
        instance.wait_until_running() # Wait until the instance reaches the "running" state
        instance.load() # Refresh the instance object to get the latest information
        instance_id = instance.id # Retrieve the instance ID and public IP address
        public_ip = instance.public_ip_address
        self.add_worker(public_ip)
        return public_ip
    
    def find_worker_node(self):
        ip = None
        while ip is None:
            for worker_ip in self.workers:
                    ip = self.ask_worker_node_to_process_new_task(worker_ip)
            if ip is None and len(self.workers) < 5:
                ip = self.create_new_worker_node()
        
        # update other manager
        payload = WorkerStatusModel(worker_ip=ip)
        json_payload = json.dumps(payload)
        headers = {
            "Content-Type": "application/json"
        }
        url = f'http://{self.other_manager_ip}/{configuration.add_worker_endpoint}'
        
        return ip
    
    # TODO check which worker is avaiable and update other manager that it is taken
    def doTask(self):
        worker = self.find_worker_node()
        if worker == None:
            #worker = new worker
            return True
        #send http post to worker