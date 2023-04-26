
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
        result : bool = self.db.entry(date, guid, parking_lot, plate)
        
        # if already guid exist for different car
        while not result:
            guid = str(uuid.uuid4())
            date = str(datetime.now())
            result : bool = self.db.entry(date, guid, parking_lot, plate)
        
        return  guid;
    
    def exit(self, ticketId):
        try:
            plate, parking_lot, entry_time = self.db.exit(ticketId)
        except Exception as e:
            print("Error: {}".format(str(e)))
            return None, None, None, None
        
        date_time_entry_obj = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S.%f')
        parked_time = datetime.now() - date_time_entry_obj
        parked_hours = parked_time.total_seconds() / 3600
        charge = parked_hours * 10

        return plate, parked_time, parking_lot, charge