import hashlib
from fastapi import FastAPI

app = FastAPI()

@app.put("/process_task")
def process_task(task: dict) -> dict:
    task_id = task["task_id"]
    buffer = task["buffer"]
    iterations = task["iterations"]
    result = work(buffer, iterations)
    return {"task_id": task_id, "result": result}

def work(buffer, iterations):
    output = hashlib.sha512(buffer).digest()
    for i in range(iterations - 1):
        output = hashlib.sha512(output).digest()
    return output