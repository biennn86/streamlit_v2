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

    def get_demo(self):
        df = self.anlytics.get_merge_data()
        self.services = WarehouseAnalyzer(df)
        ka = self.services.analyze_all_warehouses()
        return ka

        