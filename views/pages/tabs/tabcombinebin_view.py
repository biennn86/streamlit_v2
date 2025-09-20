import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController
from services.helper_services import normalize_data_upper

class TabCombineBinView:
    #Lấy data từ controller
    # def __init__(self, analytics_controller: AnalyticsController):
    #     self.analytics_controller = analytics_controller

    #Lấy data từ state
    def __init__(self, data_combinebin, datetime_current):
        self.data_combinebin = data_combinebin
        self.datetime_current = datetime_current

    def render(self) -> None:
        #Lấy data từ controller
        # self.df = self.analytics_controller.get_combinebin()
        # date_time = self.analytics_controller.get_datetime_current()

        #Lấy data từ state
        self.df = self.data_combinebin
        date_time = self.datetime_current

        cont_combinebin = st.container(border=StatusBorder.BORDER.value)
        title_combinebin = cont_combinebin.container(border=StatusBorder.BORDER.value)
        combinebin = cont_combinebin.container(border=StatusBorder.BORDER.value)

        with title_combinebin:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">COMBINE BIN {date_time}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

            # col1, col2, col3 = title_combinebin.columns([1, 10, 1])
            # with col2:
            #     st.html(f"<span class='title_commbinebin'</span>")
            #     st.subheader(f"COMBINE BIN {date_time}")
                
        with combinebin:
            st.html(f"<span class='df_combinebin'</span>")
            df_combinebin = self._edit_display_dfcombinebin_view()
            hight = 700
            if len(df_combinebin)<=15:
                hight = None
            st.dataframe(df_combinebin, hide_index=True, height=hight, use_container_width=True)

    def _edit_display_dfcombinebin_view(self) -> pd.DataFrame:
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
                   'location': 'From Location',
                   'to_location': 'To Location'
                   }, inplace=True)
        
        df = normalize_data_upper(df)

        return df