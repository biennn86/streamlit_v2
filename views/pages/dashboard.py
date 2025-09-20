import streamlit as st

# Import project components
from models.inventory_model import InventoryModel
from models.analytics_model import AnalyticsModel
from services.warehouse_services import WarehouseAnalyzer
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from controllers.location_controller import LocationController
from controllers.masterdata_controller import MasterdataController



from core.app_manager import AppManager
from controllers.user_controller import UserController
from controllers.dashboard_controller import DashboardController
from config.settings import AppConfig

from views.pages.tabs.tabdashboard_view import TabDashboardView
from views.pages.tabs.tabemptyloc_view import TabEmptyLocView
from views.pages.tabs.tabmixup_view import TabMixupView
from views.pages.tabs.tabcombinebin_view import TabCombineBinView
from views.pages.tabs.tabdataviewer_view import TabDataViewer

from views.components.sidebar_menu import sidebar_create_location, sidebar_import_files_inventory, sidebar_update_masterdata

class DashboardView:
    def __init__(self):
        #Khỏi tạo Model
        inventory_model = InventoryModel()
        analytics_model = AnalyticsModel(inventory_model)
        analytics_services = WarehouseAnalyzer(analytics_model)

        #Khỏi tạo controller
        inventory_controller = InventoryController(inventory_model)
        analytics_controller = AnalyticsController(analytics_model, analytics_services)
        dashboard_controller = DashboardController(inventory_controller, analytics_controller)

        #Khởi tạo state
        self.app_manager = AppManager()
        self.user_controller = self.app_manager.get_controller(UserController)
        self.dashboard_controller = dashboard_controller
        # self.dashboard_controller = self.app_manager.get_controller(DashboardController)


    def get_data(self):
        self.dashboard_controller.get_dashboard_data()
        data =  self.dashboard_controller.state.dashboard_data
        return data
    
    def location(self):
        create_location = sidebar_create_location()
        if create_location:
            LocationController().create_location()

    def import_masterdata(self):
        file_maserdata = sidebar_update_masterdata()
        if file_maserdata:
            MasterdataController().import_masterdata(file_maserdata)

    def import_inventory_files(self):
        files_inventory_import = sidebar_import_files_inventory()
        status_file_uploader = self.dashboard_controller.state.get(AppConfig.StateKeys.FILE_UPLOADER, False)
        if all([files_inventory_import, status_file_uploader]):
            is_valid, meesage, df = self.dashboard_controller.inventory_controller.import_file(files_inventory_import)
            st.toast(meesage, icon="ℹ️")
            

            if not is_valid:
                st.stop()

    def render(self):
        self.location()
        self.import_masterdata()
        self.import_inventory_files()

        #====================================
        data = self.get_data()
        datetime_current = data.get('datetime_current', None)
        data_chart = data.get('chart', {})
        data_emptyloc = data.get('emptyloc', {})
        data_mixup = data.get('mixup', {})
        data_combinebin = data.get('combinebin', {})
        data_current = data.get('current_data', {})
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 DashBoard", "📋 Empty Loc", "🔢 Mixup", "⚙️ Combine Bin", "📊 Analytics", "📋 Data Viewer"])

        with tab1:
            TabDashboardView(data_chart=data_chart, datetime_current=datetime_current).render()
        with tab2:
            TabEmptyLocView(data_emptyloc=data_emptyloc, datetime_current=datetime_current).render()
        with tab3:
            TabMixupView(data_mixup=data_mixup, datetime_current=datetime_current).render()
        with tab4:
            TabCombineBinView(data_combinebin=data_combinebin, datetime_current=datetime_current).render()
        with tab5:
            pass
        with tab6:
            TabDataViewer(data_current=data_current, datetime_current=datetime_current).render()

