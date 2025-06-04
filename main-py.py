import streamlit as st
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import project components
from models.inventory import InventoryModel
from models.analytics import AnalyticsModel
from services.warehouse_services import WarehouseAnalyzer
from controllers.inventory_controller import InventoryController
from controllers.analytics_controller import AnalyticsController
from views.dashboard_view import DashboardView

def main():
    """Main application function."""
    try:
        #Khỏi tạo Model
        inventory_model = InventoryModel()
        analytics_model = AnalyticsModel(inventory_model)
        # services = WarehouseAnalyzer()

        #Khỏi tạo controller
        inventory_controller = InventoryController(inventory_model)
        analytics_controller = AnalyticsController(analytics_model)

        #Khỏi tạo view
        dashboard = DashboardView(inventory_controller, analytics_controller)
        
        #Render main dashboard
        dashboard.render()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {str(e)}")
        st.error("Check the console for more details.")

if __name__ == "__main__":
    main()
