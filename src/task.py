from pydantic import BaseModel


class Task(BaseModel):
    
    def __init__(self):
        self.id :str
        self.buffer :bytes
        self.iterations :int