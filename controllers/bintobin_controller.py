import logging
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT, ImportFileStatus
from models.inventory_model import InventoryModel
from models.bintobin_model import BintobinModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BintobinController:
    def __init__(self, bintobin_model: BintobinModel):
        self.bintobin_model = bintobin_model

    def import_file_tonkho_prime(self, link_file)-> Tuple[bool, str]:
        self.df_tonkho = self.bintobin_model.real_file_import_inv_csv(link_file)
        return self.df_tonkho
    
    def import_file_demand(self, link_file)-> Tuple[bool, str]:
        self.df_demand = self.bintobin_model.read_file_demand(link_file)
        return self.df_demand
    
    def run_bintobin(self, df_tonkho, df_demand):
        self.df_bintobin = self.bintobin_model.process_bintobin(df_tonkho, df_demand)
        return self.df_bintobin
