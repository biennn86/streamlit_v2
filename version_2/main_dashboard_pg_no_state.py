import streamlit as st
import logging

import sys
import os

#=======================================
# Thêm thư mục gốc (thư mục cha) vào sys.path
# __file__ là path của main.py, dirname lấy thư mục chứa nó, dirname tiếp để ra thư mục cha
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bây giờ có thể import models
import models
# Hoặc từ models import ...
#=========================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import project components
from models.inventory_model import InventoryModel
from models.analytics_model import AnalyticsModel
from services.warehouse_services import WarehouseAnalyzer
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from version_2.dashboard_view import DashboardView

def main(): 
    """Main application function.
        Dùng khi lần đầu tiên học dependance injection
        Chưa có state
    """
    # try:
    #Khỏi tạo Model
    inventory_model = InventoryModel()
    analytics_model = AnalyticsModel(inventory_model)
    analytics_services = WarehouseAnalyzer(analytics_model)

    #Khỏi tạo controller
    inventory_controller = InventoryController(inventory_model)
    analytics_controller = AnalyticsController(analytics_model,analytics_services)

    #Khỏi tạo view
    dashboard = DashboardView(inventory_controller, analytics_controller)
    
    #Render main dashboard
    dashboard.render()
    # except Exception as e:
    #     logger.error(f"Application error: {e}")
    #     st.error(f"An error occurred: {str(e)}")
    #     st.error("Check the console for more details.")

if __name__ == "__main__":
    main()
