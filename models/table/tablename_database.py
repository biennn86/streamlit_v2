from models.database_model import DatabaseManager

class TableNameInventory(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "inventory"

class TableNameMasterdata(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "master_data"

class TableNameLocation(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "master_location_new"

class TableNameUser(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "user"
