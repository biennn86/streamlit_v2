import streamlit as st
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController
from services.helper_services import normalize_data_upper

class TabMixupView:
    #Lấy data từ controller
    # def __init__(self, analytics_controller: AnalyticsController):
    #     self.analytics_controller = analytics_controller

    #Lấy data từ state
    def __init__(self, data_mixup, datetime_current):
        self.data_mixup = data_mixup
        self.datetime_current = datetime_current

    def render(self):
        #Lấy data từ controller
        # df = self.analytics_controller.get_mixup()
        # date_time = self.analytics_controller.get_datetime_current()

        #Lấy data từ mixup
        df = self.data_mixup
        date_time = self.datetime_current

        cont_mixup = st.container(border=StatusBorder.BORDER.value)
        title_mixup = cont_mixup.container(border=StatusBorder.BORDER.value)
        mixup = cont_mixup.container(border=StatusBorder.BORDER.value)

        with title_mixup:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">BIN MIXUP {date_time}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

            # col1, col2, col3 = title_mixup.columns([1, 10, 1])
            # with col2:
            #     st.html(f"<span class='title_mixup'</span>")
            #     st.subheader(f"BIN MIXUP {date_time}")
                
        with mixup:
            st.html(f"<span class='df_mixup'</span>")
            st.dataframe(self._edit_display_df(df), hide_index=True, use_container_width=True)

    def _edit_display_df(self, df_mixup):
        #lấy cột cần hiển thị
        df_mixup = df_mixup[['date', 'location', 'gcas', 'batch', 'description', 'status', 'qty', 'pallet']]
        #viết hoa chữ cái đầu name columns
        df_mixup.columns = [str(col).capitalize() for col in df_mixup.columns]
        #Đánh lại số index
        df_mixup.index = range(1, len(df_mixup)+1)
        #viết hoa data string, object trong df
        df_mixup = normalize_data_upper(df_mixup)

        return df_mixup