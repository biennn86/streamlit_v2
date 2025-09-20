import logging
import streamlit as st
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional

from models.analytics_model import AnalyticsModel
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
        date_time_curr = self.anlytics.get_datatime_current()
        return date_time_curr
    
    def get_all_chart(self) -> Dict[str, Any]:
        df_merge = self.anlytics.get_merge_data()
        self.services.set_df_merge(df_merge)
        dict_all_chart = self.services.get_chart_for_dashboard()
        return dict_all_chart
    
    def get_mixup(self) -> pd.DataFrame:
        df_mixup = self.services.get_mixup()
        return df_mixup
    
    def get_empty_location(self) -> pd.DataFrame:
        df_empty_loc = self.services.get_empty_location()
        return df_empty_loc
    
    def get_combinebin(self) -> pd.DataFrame:
        df_combinebin = self.services.get_combinebin()
        return df_combinebin
    
    def get_current_df_data(self) -> pd.DataFrame:
        """Lưu ý: df_data trong services đã được chuẩn hóa.
            Nghĩa là đưa về chữ thường hết đối với cột là string/object
            Còn df_data_merge ở trong analytics là df_data thô lấy từ database ra

            Phương thức này dùng để hiển thị cho tab dataviewer
        """
        df_curr = self.services.get_df_merge()
        return df_curr