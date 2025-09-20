from typing import List, Tuple, Dict, Any, Optional
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from core.base_state_controller import BaseStateController
from config.settings import AppConfig

class DashboardController(BaseStateController):
    """Đưa data vào state, cung cấp cho view"""
    def __init__(self, inventory_controller: InventoryController, analytics_controller: AnalyticsController):
        super().__init__()
        self.analytics_controller = analytics_controller
        self.inventory_controller = inventory_controller

    def get_default_state(self):
        """Giá trị mặc định cho dashboard state"""
        return {
            AppConfig.StateKeys.DASHBOARD_DATA: {},
        }

    def get_dashboard_data(self):
        """Lấy dữ liệu cho dashboard"""
        #Sau khi chọn upload file mới thì sự kiện on_change sẽ đổi status của file_uploader trong state thành True
        #Hàm sẽ vào để lấy data mới nhất, sau đó đổi status file_uploader thành False để lấy data trong state
        #Phải check thêm đk data_dashoard trong state có chưa để lần chạy đầu tiên sẽ vào lấy data cuối cùng được upload,
        #hiển thị lên dashboard vì lúc đó status file_uploader đang là False
        
        data_dashboard_in_state = self.state.get(AppConfig.StateKeys.DASHBOARD_DATA, {})
        status_file_uploader = self.state.get(AppConfig.StateKeys.FILE_UPLOADER, False)
        if any([not data_dashboard_in_state, status_file_uploader]):
            # Lấy các loại dữ liệu khác nhau
            data = {
                "chart": self.analytics_controller.get_all_chart(),
                "datetime_current": self.analytics_controller.get_datetime_current(),
                "mixup": self.analytics_controller.get_mixup(),
                "emptyloc": self.analytics_controller.get_empty_location(),
                "combinebin": self.analytics_controller.get_combinebin(),
                "current_data": self.analytics_controller.get_current_df_data()
            }
            #Cập nhật lại status file_uploader là False để không vào lấy data mới
            self.state.set(AppConfig.StateKeys.FILE_UPLOADER, False)
            # Lưu vào state để cache
            self.state.set(AppConfig.StateKeys.DASHBOARD_DATA, data)
            # return data