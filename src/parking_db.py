from datetime import datetime
import sqlite3

class DatabaseCreator:
    
    def __init__(self, db_name):
        self.table_name = 'cars'
        self.db_name = db_name
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # delete
        c.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        
        # Create tables and define schema here
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                enty_hour TEXT NOT NULL,
                parking_lot TEXT NOT NULL,
                plate TEXT NOT NULL
            )
        ''')
        
        # Add more tables and schema as needed
        
        conn.commit()
        conn.close()
        
    def entry(self, date:str, guid:str, parking_lot:str, plate:str):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute(f"SELECT * FROM {self.table_name}")
        data = c.fetchall()
        print(data)
        
        c.execute(f"SELECT id FROM {self.table_name} WHERE id = ?", (guid,))
        result = c.fetchone()
        print('checking if id ', guid, 'exist in db and the answer is ', result)
        if result is not None:
            return False
        
        # Insert guid
        print('trying to insert',guid,date,parking_lot)
        c.execute(f"INSERT INTO {self.table_name} (id, enty_hour, parking_lot, plate) VALUES (?, ?, ?, ?)", (guid, f"{date}", parking_lot, plate))
        conn.commit()
        # Close the connection
        conn.close()
        return True
    
    def exit(self, guid:str):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute(f"SELECT id FROM {self.table_name} WHERE id = ?", (guid,))
        result = c.fetchone()
        print('checking if id ', guid, 'exist in db and the answer is ', result)
        if result is None:
            return None, None, None
        
        c.execute(f"SELECT plate,parking_lot,enty_hour FROM {self.table_name} WHERE id = ?", (guid,))
        result = c.fetchone()
        plate, parking_lot, entry_time = result
        c.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (guid,))

        return plate, parking_lot, entry_time