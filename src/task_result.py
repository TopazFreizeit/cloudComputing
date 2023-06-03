from pydantic import BaseModel


class TaskResult(BaseModel):
    def __init__(self, id: str , output: bytes):
        self.id :str
        self.output :bytes