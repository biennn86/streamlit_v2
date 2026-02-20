from typing import List, Optional, Dict, Union
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import re
#------------


@dataclass
class RackConfig:
	"""Cấu hình để generate rack locations"""
	name_rack: Union[str, list]
	from_bin: Union[int, list]
	to_bin: int
	level_config: Dict[str, int] # Mapping tầng -> level, VD: {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
	rack_system_type: str
	location_storage_type: str
	zone: str
	location_category: str
	location_product_category: str
	location_hight: str
	name_warehouse: str
	location_usage_type: Optional[Dict[str, int]] = field(default_factory=dict) #key vị trí change type, value là type
	list_bin_ho: Optional[List[int]] = field(default_factory=list)
	stack_limit: Optional[int] = 1
	is_active: Optional[Dict[int, list]] = 1 #Truyền vào 1 dict. Key là vị trí, value là tầng cần block. Giá trị mặc định là 1 (active)
	status_location: Optional[str] = "OK" #Dựa vào is_active để trả về status_location mong muốn
	note: Optional[str] = None #
	
	
	def __post_init__(self):
		if isinstance(self.from_bin, int):
			if self.from_bin > self.to_bin:
				raise ValueError(f"from_bin '{self.from_bin}' lớn hơn to_bin '{self.to_bin}'")
			
@dataclass
class FloorConfig:
	"""Cấu hình để generate floor locations"""
	location_name: list
	location_system_type: str
	rack_system_type: str
	location_storage_type: str
	zone: str
	location_category: str
	location_product_category: str
	name_warehouse: str
	pallet_capacity: int
	stack_limit: Optional[int] = 1
	is_active: Optional[list] = 1 #Truyền vào list vị trí cần block
	status_location: Optional[str] = "OK" # Dựa vào is_active để trả về status_location mong muốn
	note: Optional[str] = None
	
	def __post_init__(self):
		pass
	
@dataclass
class Location:
	"""Đại diện cho một location trong kho"""
	location: str
	location_system_type: str
	location_usage_type: str
	rack_system_type: str
	rack_usage_type: str
	location_storage_type: str
	zone: str
	location_category: str
	location_product_category: str
	name_rack: str
	bayslot: int
	level: str
	location_hight: str
	name_warehouse: str
	pallet_capacity: int
	stack_limit: int
	foot_print: int
	is_active: Optional[int] = 1
	status_location: Optional[str] = "OK"
	note: Optional[str] = None
	
	def to_dict(self) -> dict:
		"""Chuyển đổi sang dictionary"""
		return {
			'location': self.location,
			'location_system_type': self.location_system_type,
			'location_usage_type': self.location_usage_type,
			'rack_system_type': self.rack_system_type,
			'rack_usage_type': self.rack_usage_type,
			'location_storage_type': self.location_storage_type,
			'zone': self.zone,
			'location_category': self.location_category,
			'location_product_category': self.location_product_category,
			'name_rack': self.name_rack,
			'bayslot': self.bayslot,
			'level': self.level,
			'location_hight': self.location_hight,
			'name_warehouse': self.name_warehouse,
			'pallet_capacity': self.pallet_capacity,
			'stack_limit': self.stack_limit,
			'foot_print': self.foot_print,
			'is_active': self.is_active,
			'status_location': self.status_location,
			'note': self.note
		}
		
	def __str__(self) ->str:
		return f"{self.location} | {self.location_system_type} | {self.location_usage_type} | {self.rack_system_type} | {self.rack_usage_type} | {self.location_storage_type} | Level:{self.level} | Pallet:{self.pallet_capacity}"
	
class LocationGenerator:
	"""Generator để tạo locations từ config"""
	
	def __init__(self):
		self.locations: List[Location] = []

	#===================================Method Racks======================================
	@staticmethod
	def get_name_rack(list_bin_ho: list, level: str, rack_num: int, name_rack: str) -> str:
		"""
		Xác định name_rack
		- Nếu rack_num nằm trong list_bin_ho và tầng là A thì đổi name_rack thành HO
		- Ngược lại giữ nguyên name_rack
		"""
		if (rack_num in list_bin_ho) and (level=="A"):
			return f"HO{name_rack}"
		else:
			return name_rack

	@staticmethod
	def get_location_code(name_rack: str, rack_num: int, level: str) -> str:
		"""
		Xác định location_code
		- Nếu name_rack là HO thì location_code không có level. VD HOFA25
		- Ngược lại trả về location_code như bình thường. VD FA25A
		"""
		if name_rack.startswith("HO"):
			return f"{name_rack}{rack_num:02d}"
		else:
			return f"{name_rack}{rack_num:02d}{level}"

	@staticmethod
	def get_str_level(level: str) -> str: #A1, B1
		"""
		Xác định tầng của location
		- Nếu tầng có số phía sau -> trả về chữ cái trước số
		- Nếu không có số phía sau, trả về tầng đó
		Việc xác định tầng chỉ để lấy data cho cột level. Còn tầng location vẫn giữ nguyên
		"""
		level_str = re.search(r'[a-zA-Z]', level).group()
		if level_str:
			return level_str
		else:
			return level
		
	@staticmethod
	def get_location_system_type(level: str) -> str:
		"""
		Xác định type_rack dựa vào tầng
		- Tầng A: PF (Pick Face)
		- Tầng B trở lên: HR (High Rack)
		"""
		if level.startswith('A'):  # A, A1, A2
			return "PF"
		else:
			return "HR"
			
	@staticmethod
	def get_location_usage_type(location_usage_type: dict, rack_num: int, system_type: str) -> str:
		"""
		Xác định type_usage dựa vào vị trí rack và dict từ location_usage_type nhập đầu vào
		- Nếu vị trí có trong dict thì trả về value của dict 
		- Nếu không có thì trả về location_system_type
		Chỉ dành cho những rack đặc biệt như G10 vị trí 10-12 dùng lưu hàng Reject
		"""
		return location_usage_type.get(rack_num, system_type)
	
	@staticmethod
	def get_rack_usage_type(name_rack: str, rack_system_type: str, level: str) -> str:
		"""
		Xác định type_rack đang sử dụng hiện tại 
		- Check rack_system_type = DB và len(level) = 2 -> ST.
		Đây là vị trí rack DB nhưng chuyển mục đích sử dụng sang ST 
		- Nếu name_rack là HO thì trả về HO
		- Nếu không thõa mãn thì trả về rack_system_type
		"""
		if (rack_system_type == "DB" and len(level) == 2):
			return "ST"
		elif name_rack.startswith("HO"):
			return "HO"
		else:
			return rack_system_type
			
	@staticmethod
	def get_bayslot(rack_num: int) -> str:
		"""
		Trả về vị trí rack đang tạo
		"""
		return f"{rack_num:02d}" if rack_num is not None else None
	
	@staticmethod
	def get_pallet_capacity(rack_system_type: str, rack_usage_type: str, level: str) -> int:
		"""
		Xác định số pallet mà vị trí đó lưu trữ
		Nếu type DB -> 2 
		Nếu type ST -> 1 
		Nếu type SV -> 1 
		Nếu type OB tầng A -> 4
		Nếu type OB tầng AT, AN -> 2
		Nếu rack_usage_type là HO thì dựa vào rack_system_type để trả về số pallet tương ứng
		"""
		if rack_usage_type.startswith("HO"):
			if rack_system_type in ["DB"]:
				return 2
			elif rack_system_type in ["OB"] and level.startswith("A"):
				return 2
			elif rack_system_type in ["ST", "SV"]:
				return 1 
			else:
				raise ValueError(f"rack_system_type {rack_system_type} không hợp lệ")
		else:
			if rack_usage_type in ["OB"] and level.startswith("A"):
				return 2
			elif rack_usage_type in ["DB", "OB"]:
				return 2
			elif rack_usage_type in ["ST", "SV"]:
				return 1 
			else:
				raise ValueError(f"rack_usage_type {rack_usage_type} không hợp lệ")

	@staticmethod
	def get_is_activate(is_active: any, bin_num: any, level: str) -> int:
		"""
		Xác định active cho location. Kết quả trả về chỉ 2 giá trị 0 (không còn sử dùng), 1 (còn sử dụng)
		Nếu is_active là 1 thì trả về 1
		Nếu khác 1 thì dựa vào dict agument. Nếu bin và level vị trí cần tạo nằm trong dict thì trả về 0
		Vì agument dict là truyền vào vị trí và tầng cần được block
		"""
		if is_active == 1:
			return 1
		elif is_active == 0:
			return 0
		else:
			if all([bin_num in is_active.keys(), any(level in values_list for values_list in is_active.values())]):
				return 0
			else:
				return 1

	@staticmethod
	def get_status(is_active: int, status_location: str) -> str:
		"""
		Xác định status_location location khi tạo
		is_active ở đây là is_active sau khi đã get_is_activate()
		Nếu is_active là 1 trả về OK
		Nếu khác 1 trả về LOCK
		Còn HLOD chưa xác định vì chưa gặp trong vận hành
		"""
		if is_active == 0:
			return KeyLoc.Stauts_Location.LOCK
		else:
			return status_location
	
	@staticmethod
	def get_footprint(pallet_capacity: int, stack_limit: int) -> int:
		"""
		Xác định footprint của location 
		footprint = papallet_capacity * stack_limitlimit
		"""
		return pallet_capacity * stack_limit
		
	def generate_from_rack_config(self, config_rack: RackConfig) -> List[Location]:
		"""	Generate locations từ một config_rack
			Có 2 kiểu tạo location rack trong function này
			Kiểu 1: Tạo theo kiểu đối với các rack đặc biệt như HO vì vị trí tạo không liền mạch nhau, ví dụ 10, 11, 20, 21
			Kiểu này name_rack sẽ nhận vào 1 list tên rack
			from_bin sẽ nhận vào 1 list bin
			Và sẽ tạo vị trí như rack thông thường. Thay đổi nhỏ ở method name_rack và thuộc tính name_rack trong class Location
			Kiểu 2: Tạo rack khi nhập rack, form_bin, to_bin như thiết kế ban đầu
			Lưu ý: Phương thức check form_bin, to_bin trong class RackConfig có thêm 1 điều kiện if để check from_bin có phải là int không
			tránh báo lỗi.
			Khai báo Union[str, list] cho name_rack, Union[int, list] cho from bin ở RackConfig
			Còn lại đều như thiết kế ban đầu
		"""
		generated_racks = []
		
		if isinstance(config_rack.name_rack, list) and isinstance(config_rack.from_bin, list):
			for name_rack_ho in config_rack.name_rack:
				for rack_num in config_rack.from_bin:
					for str_level, num_level in config_rack.level_config.items():
						#Xác định tầng location
						level = self.get_str_level(str_level)
						#Xác định name_rack
						name_rack = self.get_name_rack(config_rack.list_bin_ho, level, rack_num, name_rack_ho)
						#Tạo location code: FA01D, B102A
						location_code = self.get_location_code(name_rack, rack_num, str_level)
						#Xác định location_system_type
						location_system_type = self.get_location_system_type(str_level)
						#Xác định location_usage_type
						location_usage_type = self.get_location_usage_type(config_rack.location_usage_type, rack_num, location_system_type)
						#Xác định rack_usage_type
						rack_usage_type = self.get_rack_usage_type(name_rack, config_rack.rack_system_type, str_level)
						#Xác định bayslot
						bayslot = self.get_bayslot(rack_num)
						#Xác định pallet_capacity
						pallet_capacity = self.get_pallet_capacity(config_rack.rack_system_type, rack_usage_type, str_level)
						#Xác định foot_print
						foot_print = self.get_footprint(pallet_capacity, config_rack.stack_limit)
						#Xác định is_active
						is_active = self.get_is_activate(config_rack.is_active, rack_num, str_level)
						#Xác định status
						status_location = self.get_status(is_active, config_rack.status_location)

						# Tạo location object
						location = Location(
							location = location_code,
							location_system_type = location_system_type,
							location_usage_type = location_usage_type,
							rack_system_type = config_rack.rack_system_type,
							rack_usage_type = rack_usage_type,
							location_storage_type = config_rack.location_storage_type,
							zone = config_rack.zone,
							location_category = config_rack.location_category,
							location_product_category = config_rack.location_product_category,
							name_rack = name_rack_ho,
							bayslot = bayslot,
							level = level,
							location_hight = config_rack.location_hight,
							name_warehouse = config_rack.name_warehouse,
							pallet_capacity = pallet_capacity,
							stack_limit = config_rack.stack_limit,
							foot_print = foot_print,
							is_active = is_active,
							status_location = status_location,
							note = config_rack.note
							)
						generated_racks.append(location)
						self.locations.append(location)
		else:
			for rack_num in range(config_rack.from_bin, config_rack.to_bin + 1):
				for str_level, num_level in config_rack.level_config.items():
					#Xác định tầng location
					level = self.get_str_level(str_level)
					#Xác định name_rack
					name_rack = self.get_name_rack(config_rack.list_bin_ho, level, rack_num, config_rack.name_rack)
					#Tạo location code: FA01D, B102A
					location_code = self.get_location_code(name_rack, rack_num, str_level)
					#Xác định location_system_type
					location_system_type = self.get_location_system_type(str_level)
					#Xác định location_usage_type
					location_usage_type = self.get_location_usage_type(config_rack.location_usage_type, rack_num, location_system_type)
					#Xác định rack_usage_type
					rack_usage_type = self.get_rack_usage_type(name_rack, config_rack.rack_system_type, str_level)
					#Xác định bayslot
					bayslot = self.get_bayslot(rack_num)
					#Xác định pallet_capacity
					pallet_capacity = self.get_pallet_capacity(config_rack.rack_system_type, rack_usage_type, str_level)
					#Xác định foot_print
					foot_print = self.get_footprint(pallet_capacity, config_rack.stack_limit)
					#Xác định is_active
					is_active = self.get_is_activate(config_rack.is_active, rack_num, str_level)
					#Xác định status
					status_location = self.get_status(is_active, config_rack.status_location)
				
					# Tạo location object
					location = Location(
						location = location_code,
						location_system_type = location_system_type,
						location_usage_type = location_usage_type,
						rack_system_type = config_rack.rack_system_type,
						rack_usage_type = rack_usage_type,
						location_storage_type = config_rack.location_storage_type,
						zone = config_rack.zone,
						location_category = config_rack.location_category,
						location_product_category = config_rack.location_product_category,
						name_rack = config_rack.name_rack,
						bayslot = bayslot,
						level = level,
						location_hight = config_rack.location_hight,
						name_warehouse = config_rack.name_warehouse,
						pallet_capacity = pallet_capacity,
						stack_limit = config_rack.stack_limit,
						foot_print = foot_print,
						is_active = is_active,
						status_location = status_location,
						note = config_rack.note
						)
					generated_racks.append(location)
					self.locations.append(location)
				
		return generated_racks

	def generate_from_rack_configs(self, configs_rack: List[RackConfig]) -> List[Location]:
		"""Generate locations từ nhiều configs"""
		all_locations = []
		for config in configs_rack:
			locations = self.generate_from_rack_config(config)
			all_locations.extend(locations)
		return all_locations
	#==========================================================================================
	#=====================Method Floor=========================================================

	@staticmethod
	def get_bayslot_floor() -> int:
		"""Xác định bayslot location floor"""
		return 99

	@staticmethod
	def get_level_floor(location_code: str, location_storage_type: str) -> any:
		"""
		Xác định level của location 
		- Mặc định vị trí floor có level=0
		- Trong các kho cooling3, pf5 có rack. Nên nếu storage_type là rack* thì
		cắt phải 2 ký tự, nếu trong 2 ký tự đó có số thì lấy phần chữ, nếu không thì lấy số sau cùng
		vì rack trong 2 kho này chưa có A1, B1, A2, B2 
		"""
		if location_storage_type.startswith("RACK"):
			scrap_level = location_code[-2:]
			if re.match(r'[0-9]', scrap_level):
				return re.search(r'[a-zA-Z]', scrap_level).group()
			else:
				return scrap_level[-1:]
		else:
			return 0

	@staticmethod
	def get_location_hight_floor(location_storage_type: str) -> str:
		"""
		Nếu storage_type là rack thì trả về medium
		Ngược lại trả về other 
		Vì rack trong 2 kho cooling3, pf5 chưa có rack cao 
		"""
		if location_storage_type.startswith("RACK"):
			return KeyLoc.LocHight.MEDIUM
		else:
			return KeyLoc.LocHight.OTHER
				
	@staticmethod
	def get_footprint_floor(pallet_capacity: int, stack_limit: int) -> int:
		"""Xác định foot_print"""
		if (pallet_capacity is not None) and (stack_limit is not None):
			return pallet_capacity * stack_limit
		else:
			raise ValueError(f"Lỗi khi tính foot_print floor")

	@staticmethod
	def get_is_active_floor(config_is_active: list, location: str) -> int:
		"""
		agrs: Config_floor list locaton cần block
		Nếu location có trong list config_is_active trả về 0 ngược lại trả về 1.
		Nếu list config_is_active rỗng trả về 1
		"""
		if not config_is_active:
			return 1

		if location in config_is_active:
			return 0
		else: return 1

	@staticmethod
	def get_status_location_floor(is_active: int) -> str:
		"""
		Nếu is_active = 0 -> status_location block
		Nếu is_active = 1 -> status_location ok
		"""
		if is_active == 1:
			return KeyLoc.Stauts_Location.OK
		elif is_active == 0:
			return KeyLoc.Stauts_Location.BLOCK
		else:
			raise ValueError(f"Lỗi khi xác định status_location floor. Is_Active {is_active}")

	def generate_from_floor_config(self, config_floor: FloorConfig) -> List[Location]:
		"""Generate locations từ một config_floor"""
		generated_floor = []

		for location_code in config_floor.location_name:
			#Lấy Bayslot floor
			bayslot = self.get_bayslot_floor()
			#Get level floor
			level = self.get_level_floor(location_code, config_floor.location_storage_type)
			#Get location_hight floor
			location_hight = self.get_location_hight_floor(config_floor.location_storage_type)
			#Get foot_print
			foot_print = self.get_footprint_floor(config_floor.pallet_capacity, config_floor.stack_limit)
			#Get is_activate floor
			is_active = self.get_is_active_floor(config_floor.is_active, location_code)
			#Get status_location floor
			status_location = self.get_status_location_floor(is_active)
			# Tạo location object
			location = Location(
				location = location_code,
				location_system_type = config_floor.location_system_type,
				location_usage_type = config_floor.location_system_type,
				rack_system_type = config_floor.rack_system_type,
				rack_usage_type = config_floor.rack_system_type,
				location_storage_type = config_floor.location_storage_type,
				zone = config_floor.zone,
				location_category = config_floor.location_category,
				location_product_category = config_floor.location_product_category,
				name_rack = location_code,
				bayslot = bayslot,
				level = level,
				location_hight = location_hight,
				name_warehouse = config_floor.name_warehouse,
				pallet_capacity = config_floor.pallet_capacity,
				stack_limit = config_floor.stack_limit,
				foot_print = foot_print,
				is_active = is_active,
				status_location = status_location,
				note = config_floor.note
				)

			generated_floor.append(location)
			self.locations.append(location)

		return generated_floor

	def generate_from_floor_configs(self, configs_floor: List[FloorConfig]) -> List[Location]:
		"""Generate locations từ nhiều configs"""
		all_locations = []
		for config in configs_floor:
			locations = self.generate_from_floor_config(config)
			all_locations.extend(locations)
		return all_locations
		

	def get_all_locations(self) -> List[Location]:
		"""Lấy tất cả locations"""
		return self.locations

	def get_dataframe_locations(self) -> List[Dict[any, any]]:
		"""Trả về dataframe tất cả locations"""
		all_locations = []
		for loc in self.locations:
			all_locations.append(loc.to_dict())
		df_locations = pd.DataFrame(all_locations)
		# df_locations.to_excel("loc_system_created.xlsx", index=False)
		return df_locations


class KeyLoc:
	"""Key word tạo locations"""
	class LocSystemType:
		HR = 'HR'
		PF = 'PF'
		IN = 'IN'
		PICK = 'PICK'
		SHIPOUT = 'SHIPOUT'
		SCANOUT = 'SCANOUT'
		LSLPM = 'LSLPM'
		LSLRM = 'LSLRM'
		LRT = 'LRT'
		WW = 'WW'
		REJECT = 'REJECT'
		REWORK = 'REWORK'
		RETURN = 'RETURN'
		SAMP = 'SAMP'
		EXWH = 'EXWH'
		MK = 'MK'
	class RackSystemType:
		DB = 'DB'
		ST = 'ST'
		OB = 'OB'
		SV = 'SV'
		FL = 'FL'
		OTHER = 'OTHER'
	class LocStorageType:
		RACK = 'RACK'
		RACK_COOL = 'RACK_COOL'
		RACK_PF = 'RACK_PF'
		RACK_LB = 'RACK_LB'
		FLOOR = 'FLOOR'
		OTHER = 'OTHER'
	class Zone:
		WH1_RACK = 'WH1_RACK'
		WH2_RACK = 'WH2_RACK'
		WH3_RACK = 'WH3_RACK'
		WH1_WW = 'WH1_WW'
		WH2_WW = 'WH2_WW'
		WH3_WW = 'WH3_WW'
		WH1_FLOOR = 'WH1_FLOOR'
		WH2_FLOOR = 'WH2_FLOOR'
		WH3_FLOOR = 'WH3_FLOOR'
		WH1_IN = 'WH1_IN'
		WH2_IN = 'WH2_IN'
		WH3_IN = 'WH3_IN'
		WH2_SHIPOUT = 'WH2_SHIPOUT'
		WH2_SCANOUT = 'WH2_SCANOUT'
		WH2_RETURN = 'WH2_RETURN'
		WH2_REWORK = 'WH2_REWORK'
		STREAM_REJECT = 'STREAM_REJECT'
		COOL1_FLOOR = 'COOL1_FLOOR'
		COOL1_WW = 'COOL1_WW'
		COOL2_FLOOR = 'COOL2_FLOOR'
		COOL2_WW = 'COOL2_WW'
		COOL3_FLOOR = 'COOL3_FLOOR'
		COOL3_WW = 'COOL3_WW'
		COOL3_RACK = 'COOL3_RACK'
		PF1_FLOOR = 'PF1_FLOOR'
		PF1_WW = 'PF1_WW'
		PF2_FLOOR = 'PF2_FLOOR'
		PF2_WW = 'PF2_WW'
		PF3_FLOOR = 'PF3_FLOOR'
		PF3_WW = 'PF3_WW'
		PF4_FLOOR = 'PF4_FLOOR'
		PF4_WW = 'PF4_WW'
		PF5_FLOOR = 'PF5_FLOOR'
		PF5_WW = 'PF5_WW'
		PF5_RACK = 'PF5_RACK'
		LB_RACK = 'LB_RACK'
		LB_FLOOR = 'LB_FLOOR'
		LB_WW = 'LB_WW'
		LSL_PM = 'LSL_PM'
		LSL_RM = 'LSL_RM'
		LSL_IN = 'LSL_IN'
		LSL_LRT = 'LSL_LRT'
		EXWH = 'EXWH'
		SAMP = 'SAMP'
	class LocCategory:
		STORARE = 'STORARE'
		RECEIVING = 'RECEIVING'
		PICKING = 'PICKING'
		SCANOUT = 'SCANOUT'
		SHIPPING = 'SHIPPING'
		RETURN = 'RETURN'
		REWORK = 'REWORK'
		EXWH = 'EXWH'
		REJECT = 'REJECT'
		LSL = 'LSL'
		SAMP = 'SAMP'
	class LocProducCategory:
		FG_RPM = 'FG_RPM'
		MK = 'MK'
		OTHER = 'OTHER'
	class LocHight:
		HIGHT = 'HIGHT'
		MEDIUM = 'MEDIUM'
		LOW = 'LOW'
		OTHER = 'OTHER'
	class NameWarehouse:
		WH1 = 'WH1'
		WH2 = 'WH2'
		WH3 = 'WH3'
		LB = 'LB'
		LSL = 'LSL'
		STEAM = 'STEAM'
		EXWH = 'EXWH'
		PF1 = 'PF1'
		PF2 = 'PF2'
		PF3 = 'PF3'
		PF4 = 'PF4'
		PF5 = 'PF5'
		COOL1 = 'COOL1'
		COOL2 = 'COOL2'
		COOL3 = 'COOL3'
	class Stauts_Location:
		OK = 'OK'
		HOLD = 'HOLD'
		LOCK = 'BLOCK'
	class Note:
		TANG_A_LSL_LRT_DNDC = 'TANG_A_PM_DNDC'
		WW_MID_WH = 'WW_MID_WH'
		TANG_A_LSL_CA = 'TANG_A_PM_CA'
		BO_TANG_E_PCCC = 'BO_TANG_E_PCCC'
		EO_BIN = 'EO_BIN'
		BIN_SV_LRT = 'BIN_SV_LRT'
		VUONG_COT = 'VUONG_COT'
		BIN_DAMAGE = 'BIN_DAMAGE'
		BIN_SV_DAMAGE = 'BIN_SV_DAMAGE'
		LB_REJECT = 'LB_REJECT'
		LB_EO = 'LB_EO'
		DUONG_LUONG = 'DUONG_LUONG'

def create_all_locations() -> LocationGenerator:
	#Hàm này sử dụng bên file main_location. Không sử dụng ở đây
	#Vẫn giữ hàm này ở đây để giữ lại nguyên bản thiết kế ban đầu
	generator = LocationGenerator()
	
	input_configs_rack = []

	generator.generate_from_rack_configs(input_configs_rack)

	#==========FLOOR==========================================================
	input_configs_floor = []

	generator.generate_from_floor_configs(input_configs_floor)
	
	return generator
		
if __name__ == "__main__":
	pass
	# gen = create_all_locations()
	
	# In một số location mẫu
	# print("\n--- 20 Locations đầu tiên ---")
	# for i, loc in enumerate(gen.get_all_locations()[:6000], 1):
	# 	print(f"{i:3d}. {loc}")
	#Print dataframe locations
	# print(gen.get_dataframe_locations())

	'''
	Ví dụ list comprehension
	["Even" if num % 2 == 0 else "Odd" for num in range(10)]
	1. Vòng lặp lồng nhau + if-else (Biến đổi giá trị)
	Giả sử bạn có hai danh sách: một danh sách các loại quả và một danh sách các màu sắc. Bạn muốn kết hợp chúng lại, nhưng nếu là quả "Táo", bạn muốn gán nhãn "Đỏ", các quả khác gán nhãn "Khác".
	qua = ["Táo", "Ổi"]
	mau = ["Xanh", "Chín"]

	# Cấu trúc: [biến_đổi if_else for loop1 for loop2]
	ket_qua = [f"{q} {m}: Đỏ" if q == "Táo" else f"{q} {m}: Khác" for q in qua for m in mau]

	print(ket_qua)
	2. Vòng lặp lồng nhau + if lọc + if-else biến đổi
	Đây là trường hợp phức tạp hơn: Duyệt qua 2 danh sách số, chỉ lấy những cặp số có tổng lớn hơn 5, sau đó phân loại tổng đó là "Chẵn" hay "Lẻ".
	list1 = [1, 2, 3]
	list2 = [4, 5, 6]

	# logic: Duyệt qua l1, l2 -> lọc (l1+l2 > 5) -> phân loại (Chẵn/Lẻ)
	ket_qua = [
	    f"{a}+{b}={a+b} (Chẵn)" if (a + b) % 2 == 0 else f"{a}+{b}={a+b} (Lẻ)" 
	    for a in list1 
	    for b in list2 
	    if a + b > 5
	]

	for item in ket_qua:
	    print(item)
    -------------------------
    💡 Quy tắc ghi nhớ
	Để không bị nhầm lẫn khi viết list comprehension phức tạp, bạn hãy nhớ:
		Vòng lặp: Viết theo thứ tự từ ngoài vào trong (y như viết vòng for bình thường).
		if lọc (không có else): Luôn nằm ở cuối cùng.
		if-else biến đổi: Luôn nằm ở đầu (phần biểu thức trả về).
	Lời khuyên: Nếu list comprehension của bạn dài quá 2 dòng, hãy cân nhắc dùng vòng lặp for truyền thống để đồng nghiệp (hoặc chính bạn trong tương lai) dễ đọc hơn nhé!
	'''
	
				
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
