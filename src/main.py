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
async def exit(ticketId: str = Query(..., description="Ticket Id parameter")):

    plate, parked_time, parking_lot, charge = parkingService.exit(ticketId)
    if plate is None:
        return {"message": "Record with ticketId {} not found".format(ticketId)}
    return {"plate": plate, "parkedTime": str(parked_time), "parkingLot": parking_lot, "charge": charge}