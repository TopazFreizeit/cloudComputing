import json
import time
from task import Task
import hashlib
import threading
import requests
from task_result import TaskResult
import logging
import configuration

class Worker:
    
    def __init__(self, manager_ip_1:str, manager_ip_2:str):
        self.manager_ip_1:str=manager_ip_1
        self.manager_ip_2:str=manager_ip_2
        self.work_id= 1
        self.busy:bool= False
        self.last_work_time:float = 0 
    
    
    def work(self, task:Task):
        output = hashlib.sha512(task.buffer).digest()
        for i in range(task.iterations - 1):
            output = hashlib.sha512(output).digest()
        self.busy = False
        self.last_work_time = time.time()
        result = TaskResult(id=task.id, output=output)
        self.update_managers(result)
    
    def update_managers(self, result:TaskResult):
        result_json = json.dumps(result.__dict__)
        headers = {
            "Content-Type": "application/json"
        }
        #update manager 1
        url_manager1_complete_task = f'http://{self.manager_ip_1}/{configuration.complete_task_endpoint}'
        requests.post(url=url_manager1_complete_task,data=result_json, headers=headers)
        #update manager 2
        url_manager2_complete_task= f'http://{self.manager_ip_2}/{configuration.complete_task_endpoint}'
        requests.post(url=url_manager2_complete_task,data=result_json, headers=headers)
    
    def start_new_work(self, task:Task):
        self.busy = True
        thread = threading.Thread(target=self.work, args=(task,))
        thread.start()

    def check_if_idle(self):
        while True:
            time.sleep(60)
            logging.info(f'checking if i am busy and it is {self.busy}')
            if not self.busy:
                elapsed_time = time.time() - self.last_work_time
                logging.info(f"elapsed time from last time i did a work is {elapsed_time}")
                if elapsed_time >= 300:  # 5 minutes (300 seconds)
                    url_manager1 =  f'http://{self.manager_ip_2}/{configuration.remove_work}'
                    requests.get(url=url_manager1)
                    url_manager2 = f'http://{self.manager_ip_2}/{configuration.remove_work}'
                    requests.get(url=url_manager2)
    
    