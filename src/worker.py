from task import Task
import hashlib
import threading
from task_result import TaskResult

class Worker:
    
    def __init__(self, manager_ip_1:str, manager_ip_2:str):
        self.manager_ip_1:str=manager_ip_1
        self.manager_ip_2:str=manager_ip_2
        self.busy:bool= False
    
    
    def work(self, task:Task):
        output = hashlib.sha512(task.buffer).digest()
        for i in range(task.iterations - 1):
            output = hashlib.sha512(output).digest()
        
        
        
    
    def start_new_work(self, task:Task):
        self.busy = True
        thread = threading.Thread(target=self.work, args=(task,))
        thread.start()
        