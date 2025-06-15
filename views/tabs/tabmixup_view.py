import streamlit as st
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController

class TabMixupView:
    def __init__(self, analytics_controller: AnalyticsController):
        self.analytics_controller = analytics_controller

    def render(self):
        df = self.analytics_controller.get_mixup()
        date_time = self.analytics_controller.get_datetime_current()

        cont_mixup = st.container(border=StatusBorder.BORDER.value)
        title_mixup = cont_mixup.container(border=StatusBorder.BORDER.value)
        mixup = cont_mixup.container(border=StatusBorder.BORDER.value)

        with title_mixup:
            col1, col2, col3 = title_mixup.columns([1, 10, 1])
            with col2:
                st.html(f"<span class='title_mixup'</span>")
                st.subheader(f"BIN MIXUP {date_time}")
                
        with mixup:
            st.html(f"<span class='df_mixup'</span>")
            st.dataframe(df, hide_index=True, use_container_width=True)