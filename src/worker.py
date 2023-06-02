from task import Task
import hashlib

from task_result import TaskResult

class TaskWorker:
    
    def __init__(self, id):
        self.id: str = id
    
    def work(self, task:Task) -> TaskResult:
        output = hashlib.sha512(task.buffer).digest()
        for i in range(task.iterations - 1):
            output = hashlib.sha512(output).digest()
        return TaskResult(task.id, output)