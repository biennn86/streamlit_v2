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
        """Giá trị mặc định cho BinToBin state"""
        return {
            AppConfig.StateKeys.INV_BTB: None,
            AppConfig.StateKeys.DEMAND_DATA: {},
        }

    def import_file_tonkho_prime(self, link_file)-> Tuple[bool, str]:
        result = self.bintobin_model.real_file_import_inv_csv(link_file)
        if result.status == ImportFileStatus.SUCCESS:
            #Trả status file_import về False. Để không chạy vào phương thức import trong view nữa
            self.state.set(AppConfig.StateKeys.FILE_UPLOADER_INV_BTB, False)
            # Đưa tồn kho prime chạy btb vào state
            self.state.inv_btb = result.data
            return True,  f"Successfully imported inventory Prime"
        elif result.status == ImportFileStatus.INVALID:
            return False, result.error_message
        elif result.status == ImportFileStatus.SYSTEM_ERROR:
            return False, result.error_message
    
    def import_file_demand(self, link_file)-> Tuple[bool, str]:
        result = self.bintobin_model.read_file_demand(link_file)
        if result.status == ImportFileStatus.SUCCESS:
            #Trả status file_import về False. Để không chạy vào phương thức import trong view nữa
            self.state.set(AppConfig.StateKeys.FILE_UPLOADER_DEMAND, False)
            #Đưa data demand vào state
            self.state.demand_data = result.data
            return True,  f"Successfully Imported File Demand"
        elif result.status == ImportFileStatus.INVALID:
            return False, result.error_message
        elif result.status == ImportFileStatus.SYSTEM_ERROR:
            return False, result.error_message
    
    def run_bintobin_standard(self, df_tonkho, dict_demand):
        self.df_bintobin = self.bintobin_model.process_bintobin_standard(df_tonkho, dict_demand)
        self.state.set(AppConfig.StateKeys.DF_BTB,  self.df_bintobin)
        return self.df_bintobin
    
    def run_bintobin_greedy(self, df_tonkho, dict_demand):
        self.df_bintobin = self.bintobin_model.process_bintobin_greedy(df_tonkho, dict_demand)
        self.state.set(AppConfig.StateKeys.DF_BTB,  self.df_bintobin)
        return self.df_bintobin
