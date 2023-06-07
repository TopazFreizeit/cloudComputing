class Task():
    # TODO: add timestamp    
    def __init__(self, id:str, buffer:str, iterations:int, timestamp: float):
        self.id = id
        self.buffer = buffer
        self.iterations = iterations
        self.timestamp = timestamp

class TaskResult():
    def __init__(self, id: str , output: str):
        self.id = id
        self.output = output