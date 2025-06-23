import logging
import streamlit as st
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
        if "date_time_curr" not in st.session_state:
            date_time_curr = self.anlytics.get_datatime_current()
            st.session_state.date_time_curr = date_time_curr
            return date_time_curr
        else:
            return st.session_state.date_time_curr
    
    def get_all_chart(self) -> Dict[str, Any]:
        if "dict_all_chart" not in st.session_state:
            df = self.anlytics.get_merge_data()
            self.services.set_df(df)
            # self.services = WarehouseAnalyzer(df)
            dict_all_chart = self.services.get_chart_for_dashboard()
            st.session_state.dict_all_chart = dict_all_chart
            return dict_all_chart
        else:
            return st.session_state.dict_all_chart

    
    def get_mixup(self) -> pd.DataFrame:
        if "df_mixup" not in st.session_state:
            df_mixup = self.services.get_mixup()
            st.session_state.df_mixup = df_mixup
            return df_mixup
        else:
            return st.session_state.df_mixup
    
    def get_empty_location(self) -> pd.DataFrame:
        if "df_empty_loc" not in st.session_state:
            df_empty_loc = self.services.get_empty_location()
            st.session_state.df_empty_loc = df_empty_loc
            return df_empty_loc
        else:
            return st.session_state.df_empty_loc
    
    def get_combinebin(self) -> pd.DataFrame:
        if "df_combinebin" not in st.session_state:
            df_combinebin = self.services.get_combinebin()
            st.session_state.df_combinebin = df_combinebin
            return df_combinebin
        else:
            return st.session_state.df_combinebin
    
    def get_current_df_data(self) -> pd.DataFrame:
        """Lưu ý: df_data trong services đã được chuẩn hóa.
            Nghĩa là đưa về chữ thường hết đối với cột là string/object
            Còn df_data_merge ở trong analytics là df_data thô lấy từ database ra

            Phương thức này dùng để hiển thị cho tab dataviewer
        """
        if "df_data_curr" not in st.session_state:
            df_curr = self.services.get_current_df_data()
            st.session_state.df_data_curr = df_curr
            return df_curr
        else:
            return st.session_state.df_data_curr