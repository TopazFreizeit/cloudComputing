from parking_db import DatabaseCreator
from fastapi import FastAPI, Query
from parking_service import parkingService


db_service = DatabaseCreator('my_database.db')

parkingService = parkingService(db_service)
app = FastAPI()


@app.post("/entry")
async def entry(plate: str = Query(..., description="Plate Number"), 
                      parkingLot: int = Query(..., gt=0, description="Parking Lot Number")):
    guid = parkingService.entry(plate, parkingLot)
    return {"ticket_id": guid}

@app.post("/exit")
async def exit(ticketId: int = Query(..., gt=0, description="Ticket Id parameter")):
    """
    Endpoint to create an item with two query parameters
    """
    # Your code to create the item using the two query parameters
    return {"item_created": True}