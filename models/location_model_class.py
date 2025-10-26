import logging
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from models.table.tablename_database import TableNameLocation
from utils.state_utils import get_state_everywhere
from dataclasses import dataclass, field
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RackConfig:
    """Cấu hình để generate rack locations"""
    name_rack: str  # VD: B1
    from_bin: int
    to_bin: int
    level_config: Dict[str, int]  # Mapping tầng -> level, VD: {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    bin_ho: Optional[List] = None
    category_rack: str   # DB hoặc ST
    name_wh: str
    note: Optional[str] = None

    def __post_init__(self):
        if self.from_bin > self.to_bin:
            raise ValueError(f"Bin từ ({self.from_bin}) không thể lớn hơn bin đến ({self.to_bin})")

@dataclass
class Location:
    """Đại diện cho một location trong kho"""
    location: str           # VD: B102B
    type_rack: str         # HR hoặc PF
    category_rack: str          # DB hoặc ST
    type_loc: str          # DB hoặc ST
    name_wh: str           # VD: WH1
    name_rack: str         # VD: B1
    level: int             # Level của tầng
    num_pallet: int        # 2 cho DB, 1 cho ST
    stack_limit: int       # Giới hạn stack
    foot_print: int        # Foot print
    note: Optional[str] = None

    def to_dict(self) -> dict:
        """Chuyển đổi sang dictionary"""
        return {
            'location': self.location,
            'type_rack': self.type_rack,
            'cat_rack': self.category_rack,
            'type_loc': self.type_loc,
            'name_wh': self.name_wh,
            'name_rack': self.name_rack,
            'level': self.level,
            'num_pallet': self.num_pallet,
            'stack_limit': self.stack_limit,
            'foot_print': self.foot_print,
            'note': self.note,
        }
    
    def __str__(self) -> str:
        return f"{self.location} | {self.type_rack} | {self.cat_rack} | Level:{self.level} | Pallet:{self.num_pallet}"
    
class LocationGenerator:
    """Generator để tạo locations từ config"""
    
    def __init__(self):
        self.locations: List[Location] = []
        
    
    @staticmethod
    def get_type_rack(name_wh: str, tang: str) -> str:
        """
        Xác định type_rack dựa vào name_wh và level
        - name_wh == 'WH2' và level == 'A' -> PF (Pick Face)
        - name_wh != 'WH2' và level == 'A' -> PF
        - Còn lại type_rack = HR (High Rack)
        """
        NAME_WH2 = 'WH2'
        if (name_wh == NAME_WH2) and (tang.startswith('A')):  # A, A1, A2
            return "PF"
        elif (name_wh != NAME_WH2) and (tang.startswith('A')):
            return "PF"
        else:
            return "HR"
    
    @staticmethod
    def get_type_loc(name_rack: str, category_rack: str, level: str) -> str:
        """
        Xác định type_loc dựa vào category_rack hoặc name_rack
        - Nếu category_rack là DB và len(level) == 2 -> ST (trường hợp rack đôi nhưng tầng đơn)
        - Nếu name_rack là HO -> type_rack == HO
        - Còn lại type_loc == category_loc
        """
        CTGR_RACK_DB = 'DB', NAME_RACK_HO = 'HO'
        if (category_rack == CTGR_RACK_DB) and (len(level) == 2):
            return "ST"
        elif name_rack == NAME_RACK_HO:
            return "HO"
        else:
            return category_rack
        
    @staticmethod
    def get_name_rack(name_rack: str, bin_ho: List):
        """
        Xác định name_rack
        - Nếu vị trí rack là bin HO -> name_rack = HO
        - Còn lại name_rack = name_rack
        """
        if bin_ho:
            return "HO"
        else:
            return name_rack
    
    @staticmethod
    def get_num_pallet(cat_rack: str) -> int:
        """
        Xác định số pallet dựa vào cat_rack
        - DB: 2 pallets
        - ST: 1 pallet
        """
        return 2 if cat_rack == "DB" else 1
    
    def generate_from_config(self, config: RackConfig) -> List[Location]:
        """Generate locations từ một config"""
        generated = []
        
        for rack_num in range(config.from_bin, config.to_bin + 1):
            for tang, level in config.level_config.items():
                # Tạo location code: B102B
                location_code = f"{config.name_rack}{rack_num:02d}{tang}"
                
                # Xác định type_rack
                type_rack = self.get_type_rack(tang)
                
                # Xác định num_pallet
                num_pallet = self.get_num_pallet(config.cat_rack)
                
                # Tạo location object
                location = Location(
                    location=location_code,
                    type_rack=type_rack,
                    cat_rack=config.cat_rack,
                    type_loc=config.cat_rack,
                    name_wh=config.name_wh,
                    name_rack=config.name_rack,
                    level=level,
                    num_pallet=num_pallet,
                    stack_limit=config.stack_limit,
                    foot_print=config.foot_print,
                    note=config.note
                )
                
                generated.append(location)
                self.locations.append(location)
        
        return generated
    
    def generate_from_configs(self, configs: List[RackConfig]) -> List[Location]:
        """Generate locations từ nhiều configs"""
        all_locations = []
        for config in configs:
            locations = self.generate_from_config(config)
            all_locations.extend(locations)
        return all_locations

#======================================================
def create_all_locations() -> LocationGenerator:
    """Tạo tất cả locations từ dữ liệu file"""
    
    generator = LocationGenerator()
    CTGR_RACK_DB = 'DB'; CTGR_RACK_ST = 'ST'; CTGR_RACK_OB = 'OB'
    NAME_WH1 = 'WH1'; NAME_WH2 = 'WH2'; NAME_WH3 = 'WH3'
    #Tạo config rack cung cấp cho RackConfig từ đó lấy data cung cấp cho Loation
    #Locaton cung cấp cho LocationGenerator để tạo vị trí
    configs = [
        #B1 rack

    ]