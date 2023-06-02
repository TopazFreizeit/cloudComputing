from fastapi import FastAPI
from task import Task

app = FastAPI()

@app.put("/process_task")
def process_task(task: Task) -> dict:
    task_id = task.id
    buffer = task.buffer
    iterations = task.iterations
    result = work(buffer, iterations)
    return {"task_id": task_id, "result": result}
