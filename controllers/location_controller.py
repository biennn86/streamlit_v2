from models.create_location_models.main_create_location_pg import main_create_loc


class LocationController:
    def __init__(self):
        pass
    def create_location(self):
        success, number_rows_insert = main_create_loc()
        if success:
            return True,  f"Successfully imported {number_rows_insert:,} location records."
        else:
            return False, f"Failed to save location to database."