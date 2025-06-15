import logging
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional

from models.analytics import AnalyticsModel
from services.warehouse_services import WarehouseAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsController:
    """Injection AnalyticsModel, WarehoueseAnalyzer cho ra kết quả phân tích đưa lên dashboard
    """
    def __init__(self, analytics: AnalyticsModel, services: Optional[WarehouseAnalyzer]=None):
        self.anlytics = analytics
        self.services = services

    def get_datetime_current(self) -> str:
        """Lấy date time hiện tại trong analytics đã lấy
        """
        return self.anlytics.get_datatime_current()
    
    def get_all_chart(self) -> Dict[str, Any]:
        df = self.anlytics.get_merge_data()
        self.services = WarehouseAnalyzer(df)
        dict_all_chart = self.services.get_chart_for_dashboard()
        return dict_all_chart
    
    def get_mixup(self) -> pd.DataFrame:
        return self.services.get_mixup()
    
    def get_empty_location(self) -> pd.DataFrame:
        df_master_loc = self.anlytics.get_master_location()
        return self.services.get_empty_location(df_master_loc)
    
    def get_combinebin(self) -> pd.DataFrame:
        df_combinebin = self.services.get_combinebin()
        return df_combinebin
    
    def get_current_df_data(self) -> pd.DataFrame:
        return self.services.get_current_df_data()

        