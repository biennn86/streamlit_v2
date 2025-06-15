import streamlit as st
import pandas as pd
import logging
from typing import Dict, Any, Callable

from utils.constants import PAGE_CONFIG
from views.menu_appview import *
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from views.tabs.tabdashboard_view import TabDashboardView
from views.tabs.tabmixup_view import TabMixupView
from views.tabs.tabemptyloc_view import TabEmptyLocView
from views.tabs.combinebin_view import CombineBinView

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardView:
    """Main hiển thị dashboard"""
    def __init__(self, inventory_controller: InventoryController, analytics_controller: AnalyticsController):
        self.inventory_controller = inventory_controller
        self.analytics_controller = analytics_controller
        #khởi tạo tab dashboardview
        self.dashboard_view = TabDashboardView(analytics_controller)
        self.mixup_view = TabMixupView(analytics_controller)
        self.emptyloc_view = TabEmptyLocView(analytics_controller)
        self.combinebin_view = CombineBinView(analytics_controller)
        #khởi tạo class menu app
        self.menuapp = MenuApp()

    def init_page_config(self):
        st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=PAGE_CONFIG["page_icon"],
        layout=PAGE_CONFIG["layout"],
        initial_sidebar_state=PAGE_CONFIG["initial_sidebar_state"],
        menu_items=PAGE_CONFIG["menu_items"]
        )

    def render(self) -> None:
        self.init_page_config()
        #show sidebar menu
        creare_location = self.menuapp.create_location()
        upload_files = self.menuapp.import_files_inventory()
       
        if any(upload_files):
            is_valid, meesage, df = self.inventory_controller.import_file(upload_files)
            st.toast(meesage, icon="ℹ️")
            if not is_valid:
                st.stop()
            # if len(upload_files)%3==0:
            #     st.dataframe(self.inventory_controller.get_merge_data(), use_container_width=True, height=600)

         # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 DashBoard", "📋 Empty Loc", "🔢 Mixup", "⚙️ Combine Bin", "📊 Analytics", "📋 Data Viewer"])

        with tab1:
            self.dashboard_view.render()
        
        with tab2:
            self.emptyloc_view.render()
            
        with tab3:
            self.mixup_view.render()
        
        with tab4:
            self.combinebin_view.render()

#===============================================
        # dict_chart = self.analytics_controller.get_all_chart()
        # # st.dataframe(df, height=600, use_container_width=True)
        # for key, value in dict_chart.items():
        #     try:
        #         st.write(key)
        #         st.plotly_chart(value)
        #     except:
        #         st.metric(**value)
        # # st.metric(**dict_chart.block_rpm)
        # # st.plotly_chart(dict_chart.wh_total)