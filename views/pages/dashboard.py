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
        """ Lấy data cho dashboard từ controller
            Hiển thị các chức năng và các tab theo role của từng user
            Đặc biệt lưu ý:
            Phương thức self.get_data() lúc nào cũng phải nằm phía dưới phương thức self.import_inventory_files()
            Vì khi phương thức self.import_inventory_files() được kích hoạt thì sự kiện on_change trong st.file_uploader() được thực thi
            Sự kiện này sẽ đổi status file_upload trong sesson_state từ False thành True
            Và streamlit sẽ chạy lại toàn bộ code lại từ đầu, bắt đầu từ file main
            Nên để phương thức self.import_inventory_files() trước để chạy hết chức năng import_file vì lúc đó status file_upload đang là True
            Sau đó sẽ chạy tới phương thức self.get_data() trong phương thức này sẽ đổi status file_upload từ True thành False
            Để không chạy tiếp vào phương thức self.import_inventory_files() hoặc self.get_data() ở các lần rerun sau.
            Đấy là lý do phương thức self.import_inventory_files() lúc nào cũng phải ở trước phương thức self.get_data,
            mục đích để self.import_inventory_files() xử lý tiếp tục đưa data vào database hoàn tất quá trình xử lý của phương thức như đã thiết kế.
        """
        inventory_model = InventoryModel()
        analytics_model = AnalyticsModel(inventory_model)
        analytics_services = WarehouseAnalyzer(analytics_model)

        #Khởi tạo controller
        inventory_controller = InventoryController(inventory_model)
        analytics_controller = AnalyticsController(analytics_model, analytics_services)
        dashboard_controller = DashboardController(inventory_controller, analytics_controller)

        self.masterdata_controller = MasterdataController()
        self.location_controller = LocationController()


        #Khởi tạo state
        self.app_manager = AppManager()
        self.user_controller = self.app_manager.get_controller(UserController)
        self.dashboard_controller = dashboard_controller
        # self.dashboard_controller = self.app_manager.get_controller(DashboardController)

        #Get role for user
        self.role_user = self.user_controller.state.user_role


    def get_data(self):
        self.dashboard_controller.get_data_dashboard()
        self.data =  self.dashboard_controller.state.get(AppConfig.StateKeys.DASHBOARD_DATA, {})
        if self.data:
            self.datetime_current = self.data.get('datetime_current', None)
            self.data_chart = self.data.get('chart', {})
            self.data_emptyloc = self.data.get('emptyloc', {})
            self.data_mixup = self.data.get('mixup', {})
            self.data_combinebin = self.data.get('combinebin', {})
            self.data_current = self.data.get('current_data', {})
    
    def location(self):
        create_location = sidebar_create_location()
        if create_location:
            is_valid, meesage = self.location_controller.create_location()
            if is_valid:
                st.toast(meesage, icon="ℹ️")
            else:
                st.toast(meesage, icon="🚨")

    def import_masterdata(self):
        # icon="⚠️"
        # icon="🚨"
        file_maserdata = sidebar_update_masterdata()
        if file_maserdata:
            is_valid, meesage = self.masterdata_controller.import_masterdata(file_maserdata)
            if is_valid:
                st.toast(meesage, icon="ℹ️")
            else:
                st.toast(meesage, icon="🚨")

    def import_inventory_files(self):
        files_inventory_import = sidebar_import_files_inventory()
        status_file_uploader = self.dashboard_controller.state.get(AppConfig.StateKeys.FILE_UPLOADER, False)
        if all([files_inventory_import, status_file_uploader]):
            is_valid, meesage, df = self.dashboard_controller.inventory_controller.import_file(files_inventory_import)
            st.toast(meesage, icon="ℹ️")

            if not is_valid:
                st.stop()

    def render_tab_dashboard(self):
        TabDashboardView(data_chart=self.data_chart, datetime_current=self.datetime_current).render()
    
    def render_tab_emptyloc(self):
        TabEmptyLocView(data_emptyloc=self.data_emptyloc, datetime_current=self.datetime_current).render()

    def render_tab_mixup(self):
        TabMixupView(data_mixup=self.data_mixup, datetime_current=self.datetime_current).render()

    def render_tab_combinebin(self):
        TabCombineBinView(data_combinebin=self.data_combinebin, datetime_current=self.datetime_current).render()

    def render_tab_dataviewer(self):
        TabDataViewer(data_current=self.data_current, datetime_current=self.datetime_current).render()
    
    def render_full_tab(self):
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 DashBoard", "📋 Empty Loc", "🔢 Mixup", "⚙️ Combine Bin", "📊 Analytics", "📋 Data Viewer"])
        with tab1:
            self.render_tab_dashboard()
        with tab2:
            self.render_tab_emptyloc()
        with tab3:
            self.render_tab_mixup()
        with tab4:
            self.render_tab_combinebin()
        with tab5:
            pass
        with tab6:
            self.render_tab_dataviewer()

    def render(self):
        if self.role_user in ['guest']:
            self.get_data()
            tab1,  = st.tabs(["🏠 DashBoard"])
            with tab1:
                self.render_tab_dashboard()
        elif self.role_user in ['viewer']:
            self.get_data()
            tab1, tab2 = st.tabs(["🏠 DashBoard", "🔢 Mixup"])
            with tab1:
                self.render_tab_dashboard()
            with tab2:
                self.render_tab_mixup()
        elif self.role_user in ['edit']:
            self.import_masterdata()
            self.import_inventory_files()
            self.get_data()
            self.render_full_tab()
        elif self.role_user in ['admin']:
            self.location()
            self.import_masterdata()
            self.import_inventory_files()
            self.get_data()
            self.render_full_tab()

