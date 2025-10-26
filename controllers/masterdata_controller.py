from typing import List, Tuple, Dict, Any, Optional
from models.masterdata_model import MasterdataModel

class MasterdataController:
    def __init__(self):
        self.masterdata_model = MasterdataModel()

    def import_masterdata(self, link_file: str) -> Tuple[bool, str]:
        success, number_rows_insert = self.masterdata_model.save_masterdata(link_file)
        if success:
            return True,  f"Successfully imported {number_rows_insert:,} masterdata records."
        else:
            return False, f"Failed to save masterdata to database."