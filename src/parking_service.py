
import uuid
from datetime import datetime
from parking_db import DatabaseCreator


class parkingService():
    def __init__(self, db_service: DatabaseCreator):
        self.db = db_service
    
    def entry(self, plate, parking_lot):
        parking_lot = str(parking_lot)
        print(plate, parking_lot)
        
        guid = str(uuid.uuid4())
        date = str(datetime.now())
        result : bool = self.db.entry(date, guid, parking_lot)
        
        # if already guid exist for different car
        while not result:
            guid = str(uuid.uuid4())
            date = str(datetime.now())
            result : bool = self.db.entry(date, guid, parking_lot)
        
        return  guid;
    