import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController
from services.helper_services import normalize_data_upper

class CombineBinView:
    def __init__(self, analytics_controller: AnalyticsController):
        self.analytics_controller = analytics_controller

    def render(self) -> None:
        self.df = self.analytics_controller.get_combinebin()
        date_time = self.analytics_controller.get_datetime_current()

        cont_combinebin = st.container(border=StatusBorder.BORDER.value)
        title_combinebin = cont_combinebin.container(border=StatusBorder.BORDER.value)
        combinebin = cont_combinebin.container(border=StatusBorder.BORDER.value)

        with title_combinebin:
            col1, col2, col3 = title_combinebin.columns([1, 10, 1])
            with col2:
                st.html(f"<span class='title_commbinebin'</span>")
                st.subheader(f"COMBINE BIN {date_time}")
                
        with combinebin:
            st.html(f"<span class='df_combinebin'</span>")
            st.dataframe(self._edit_display_dfemptyloc_view(), hide_index=True, height=600, use_container_width=True)

    def _edit_display_dfemptyloc_view(self) -> pd.DataFrame:
        #Lấy cột cần hiển thị
        df = self.df[['date', 'gcas', 'description', 'batch', 'status', 'qty', 'pallet', 'location', 'to_location']].copy()
        #đánh lại stt
        df.index = range(1, len(df)+1)
        #reset lại index drop=False để lấy cột index rename thành stt
        df = df.reset_index(drop=False)
        #đổi tên cột
        df.rename(columns=
                  {'index': 'No',
                   'date': 'DateTime',
                   'gcas': 'Gcas',
                   'description': 'Description',
                   'batch': 'Batch',
                   'status': 'Status',
                   'qty': 'Qty',
                   'pallet': 'Pallet',
                   'location': 'From_Location',
                   'to_location': 'To_Location'
                   }, inplace=True)
        
        df = normalize_data_upper(df)

        return df