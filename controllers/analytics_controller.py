import logging
from typing import List, Tuple, Dict, Any, Optional

from models.analytics import AnalyticsModel
from services.warehouse_services import WarehouseAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsController:
    """Injection AnalyticsModel, WarehoueseAnalyzer cho ra kết quả phân tích đưa lên dashboard
    """
    def __init__(self, analytics: AnalyticsModel, services: Optional[WarehouseAnalyzer]=None):
        self.anlytics = analytics
        self.services = services

    def get_all_chart(self):
        df = self.anlytics.get_merge_data()
        self.services = WarehouseAnalyzer(df)
        dict_all_chart = self.services.get_chart_for_dashboard()
        return dict_all_chart

        