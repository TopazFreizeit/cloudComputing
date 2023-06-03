import json
import time
from sklearn.setup import configuration
from task import Task
import hashlib
import threading
import requests
from task_result import TaskResult

class Worker:
    
    def __init__(self, manager_ip_1:str, manager_ip_2:str):
        self.manager_ip_1:str=manager_ip_1
        self.manager_ip_2:str=manager_ip_2
        self.work_id= 1
        self.busy:bool= False
        self.finsh_time = 0 
    
    
    def work(self, task:Task):
        output = hashlib.sha512(task.buffer).digest()
        for i in range(task.iterations - 1):
            output = hashlib.sha512(output).digest()
        self.busy = False
        self.finsh_time = time.time()
        self.check_flag()
        self.update_manager(task,output)
    
    def update_manager(self,task:Task, output):
        # Create a TaskResult object
        result = TaskResult(id=task.id, output=output)
        # Convert TaskResult to JSON string
        result_json = json.dumps(result.__dict__)

        #update manager 1
        url_manager1_complete_task = f'http://{self.manager_ip_1}/{configuration.complete_task_endpoint}'
        requests.post(url_manager1_complete_task,task_result =result_json)

        #update manager 2
        url_manager2_complete_task= f'http://{self.manager_ip_2}/{configuration.complete_task_endpoint}'
        requests.post(url_manager2_complete_task,task_result =result_json)
    
    def start_new_work(self, task:Task):
        self.busy = True
        thread = threading.Thread(target=self.work, args=(task,))
        thread.start()

    def check_flag(self):
        while True:
            if not self.busy:
                elapsed_time = time.time() - self.finsh_time
                if elapsed_time >= 300:  # 5 minutes (300 seconds)
                    url_manager1 =  f'http://{self.manager_ip_2}/{configuration.remove_work}'
                    requests(url_manager1,self.work_id)
                    url_manager2 = f'http://{self.manager_ip_2}/{configuration.remove_work}'
                    requests(url_manager2,self.work_id)
    
    