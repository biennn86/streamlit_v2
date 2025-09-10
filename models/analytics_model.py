import logging
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd

from models.inventory_model import InventoryModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsModel:
    """Lấy data đã merge từ InventoryModel để đi phân tích
    """
    def __init__(self, inveotory: InventoryModel):
        self.inventory_model = inveotory
    
    def get_merge_data(self, date_time: Optional[str]=None) -> pd.DataFrame:
        """Lấy datamerge từ InventoryModel
        """
        try:
            self.df_merge = self.inventory_model.get_merge_data(date_time)
            return self.df_merge
        except Exception as e:
            logger.error(f"Get merge data error: {e}")
            raise
        
    def get_master_location(self) -> pd.DataFrame:
        """Lấy master location từ database thông qua InventoryModel
        """
        try:
            df_loc = self.inventory_model.get_location()
            return df_loc
        except Exception as e:
            logger.error(f"Get Master Location Error: {e}")
            raise


    def get_datatime_current(self) -> str:
        """Lấy datatime hiện tại của dataframe trong cột date
        """
        date_time = self.df_merge.iloc[1, 0].upper()
        return date_time
