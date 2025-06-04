import logging
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd

from models.inventory import InventoryModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsModel:
    """Lấy data đã merge từ InventoryModel để đi phân tích
    """
    def __init__(self, inveotory: InventoryModel):
        self.inventory_model = InventoryModel()
    
    def get_merge_data(self, date_time: Optional[str]=None) -> pd.DataFrame:
        """Lấy datamerge từ InventoryModel
        """
        try:
            df_merge = self.inventory_model.get_merge_data(date_time)
            return df_merge
        except Exception as e:
            logger.error(f"Get merge data error: {e}")
            raise
