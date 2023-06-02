from fastapi import Body, FastAPI, Query
import uuid

from manager.manager import TaskManager

app = FastAPI()

# Create an instance of TaskManager
manager = TaskManager()

@app.put("/enqueue")
def enqueue(iterations: int = Query(..., description="number of iterations", gt=0), buffer: bytes = Body(...)) -> str:
    work_id = str(uuid.uuid4())
    new_task = (work_id, buffer, iterations)
    manager.add_task(new_task)
    return work_id

@app.post("/pullCompleted")
async def exit(top: str = Query(..., description="number of getting the completed tasks")):
    return {"plate": plate, "parkedTime": str(parked_time), "parkingLot": parking_lot, "charge": charge}