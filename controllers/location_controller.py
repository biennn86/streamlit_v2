from models.location_model import *

class LocationController:
    def __init__(self):
        pass
    def create_location(self):
        success, number_rows_insert = main_createloc()
        if success:
            return True,  f"Successfully imported {number_rows_insert:,} location records."
        else:
            return False, f"Failed to save location to database."