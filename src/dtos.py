class Task():    
    def __init__(self, id:str, buffer:str, iterations:int):
        self.id = id
        self.buffer = buffer
        self.iterations = iterations

class TaskResult():
    def __init__(self, id: str , output: str):
        self.id = id
        self.output = output