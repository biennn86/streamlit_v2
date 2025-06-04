import streamlit as st
import pandas as pd
import logging
from typing import Dict, Any, Callable

from utils.constants import PAGE_CONFIG
from views.menu_appview import *
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardView:
    """Main hiển thị dashboard"""
    def __init__(self, inventory_controller: InventoryController, analytics_controller: AnalyticsController):
        self.inventory_controller = inventory_controller
        self.analytics_controller = analytics_controller
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
            # if len(upload_files)%3==0:
            #     st.dataframe(self.inventory_controller.get_merge_data(), use_container_width=True, height=600)
        df = self.analytics_controller.get_demo()
        st.dataframe(df, height=600, use_container_width=True)
        st.write(creare_location)