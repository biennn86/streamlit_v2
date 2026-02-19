import logging
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from utils.state_utils import get_state_everywhere
import datetime
from models.table.tablename_database import TableNameLocation

from models.create_location_models.model_location_pg import LocationGenerator

from models.create_location_models.location_wh1 import *
from models.create_location_models.location_wh2 import *
from models.create_location_models.location_wh3 import *
from models.create_location_models.location_pf1 import *
from models.create_location_models.location_pf2 import *
from models.create_location_models.location_pf3 import *
from models.create_location_models.location_pf4 import *
from models.create_location_models.location_pf5 import *
from models.create_location_models.location_cl1 import *
from models.create_location_models.location_cl2 import *
from models.create_location_models.location_cl3 import *
from models.create_location_models.location_label import *
from models.create_location_models.location_floor_other import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_locations() -> LocationGenerator:
	generator = LocationGenerator()

	list_location_wh1 = list_config_wh1()
	list_location_wh2 = list_config_wh2()
	list_location_wh3 = list_config_wh3()
	list_location_lb = list_config_label()
	list_location_cl = list_config_cl1() + list_config_cl2() + list_config_cl3()
	list_location_pf = list_config_pf1() + list_config_pf2() + list_config_pf3() + list_config_pf4() + list_config_pf5() 
	list_location_floor_other = list_config_floor_other()

	list_configs_location = list_location_wh1 + list_location_wh2 + list_location_wh3 + list_location_lb + list_location_pf + list_location_cl  + list_location_floor_other

	#Kiểm tra từng phần tử trong list config_location
	#Phân biệt đâu là phần tử class RackConfig và đâu là phần tử FloorConfig
	#Để dùng method generate cho đúng
	for item in list_configs_location:
		if isinstance(item, RackConfig):
			generator.generate_from_rack_config(item)
		elif isinstance(item, FloorConfig):
			generator.generate_from_floor_config(item)
		else:
			print("Đối tượng config_location chưa xác định")

	return generator

def save_location(df: pd.DataFrame) -> Tuple[bool, int]:
	"""Lưu file inventory vào database
	Args:
		df: DataFrame tổng hợp của EO, FG, RPM đã được xử lý done
	Returns:
		Boolean indicating success
	"""
	try:
		number_row_insert = TableNameLocation().insert_dataframe_new_only(df)
		logger.info(f"Saved {number_row_insert} location to database")
		return True, number_row_insert
	except Exception as e:
		logger.error(f"Error saving location: {e}")
		return False, 0
	
# if __name__ == "__main__":
def main_create_loc():
	generator_loc = create_all_locations()
	df = generator_loc.get_dataframe_locations()
	#lấy user
	state = get_state_everywhere()
	user = state.get('username', None)
	# Lấy ngày giờ hiện tại
	current_datetime = datetime.datetime.now()
	# Định dạng đối tượng datetime thành chuỗi
	formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
	df['created_at'] = formatted_string
	df['user'] = user

	# df.to_excel('location.xlsx', index=False)

	#Save to database
	return save_location(df)