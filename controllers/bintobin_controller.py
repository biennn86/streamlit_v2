import logging
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT, ImportFileStatus
from models.inventory_model import InventoryModel
from models.bintobin_model import BintobinModel

from core.base_state_controller import BaseStateController
from config.settings import AppConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BintobinController(BaseStateController):
    def __init__(self, bintobin_model: BintobinModel):
        super().__init__()
        self.bintobin_model = bintobin_model

    def get_default_state(self) -> Dict:
        """Giá trị mặc định cho user state"""
        return {
            AppConfig.StateKeys.INV_BTB: None,
            AppConfig.StateKeys.DEMAND_DATA: {},
        }

    def import_file_tonkho_prime(self, link_file)-> Tuple[bool, str]:
        self.df_tonkho = self.bintobin_model.real_file_import_inv_csv(link_file)
        self.state.set(AppConfig.StateKeys.FILE_UPLOADER_INV_BTB, False)
        return self.df_tonkho
    
    def import_file_demand(self, link_file)-> Tuple[bool, str]:
        self.df_demand = self.bintobin_model.read_file_demand(link_file)
        self.state.set(AppConfig.StateKeys.FILE_UPLOADER_DEMAND, False)
        return self.df_demand
    
    def run_bintobin_standard(self, df_tonkho, dict_demand):
        self.df_bintobin = self.bintobin_model.process_bintobin_standard(df_tonkho, dict_demand)
        self.state.set(AppConfig.StateKeys.DF_BTB,  self.df_bintobin)
        return self.df_bintobin
    
    def run_bintobin_greedy(self, df_tonkho, dict_demand):
        self.df_bintobin = self.bintobin_model.process_bintobin_greedy(df_tonkho, dict_demand)
        self.state.set(AppConfig.StateKeys.DF_BTB,  self.df_bintobin)
        return self.df_bintobin
