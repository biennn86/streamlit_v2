import streamlit as st
import pandas as pd
import logging
from typing import Dict, Any, Callable

from utils.constants import PAGE_CONFIG
from version_2.views.menu_appview import *
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from controllers.location_controller import LocationController
from controllers.masterdata_controller import MasterdataController

from views.tabs.tabdashboard_view import TabDashboardView
from views.tabs.tabmixup_view import TabMixupView
from views.tabs.tabemptyloc_view import TabEmptyLocView
from views.tabs.tabcombinebin_view import CombineBinView
from views.tabs.tabdataviewer_view import TabDataViewer

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
        self.dataviewer_view = TabDataViewer(analytics_controller)
        #khởi tạo class menu app
        self.menuapp = MenuApp()
        #khởi tạo session_state để bắt sự kiện on_change
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = False

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
        # st.title("🏭 Warehouse Inventory Management System")
        #show sidebar menu
        creare_location = self.menuapp.create_location()

        if creare_location:
            LocationController().create_location()
        
        update_masterdata =self.menuapp.update_masterdata()
        if update_masterdata:
            MasterdataController().import_masterdata(update_masterdata)

        upload_files = self.menuapp.import_files_inventory()
        st.session_state.len_uploaded_files = len(upload_files)
       
        if st.session_state.uploaded_files is None:
            """Phác thảo bắt sự kiện upload_files để clear session_state cho streamlit lấy data mới upload đi phân tích
                1. khởi tạo ss uploaded_files có data False
                2. Lúc đó sẽ bỏ qua if này và chạy xuống dưới, lấy data gần nhất trong database để analytics
                3. khi người dùng chọn uploaded_files thì ss uploaded_file sẽ update lại giá trị là None
                5. lúc đó sẽ đủ điều kiện để vào if này và đi phân tích file mới, đồng thời clear ss cũ cập nhật
                lại ss uploaded_files để tránh vào lần nữa.
                Tóm lại: sẽ bắt sự kiện ss uploaded_files là None để lấy files mới
            """
            st.session_state.clear()
            st.session_state.uploaded_files = True
            is_valid, meesage, df = self.inventory_controller.import_file(upload_files)
            st.toast(meesage, icon="ℹ️")

            if not is_valid:
                st.stop()

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
        
        with tab5:
            pass

        with tab6:
            # st.write(st.session_state)
            self.dataviewer_view.render()

#===============================================