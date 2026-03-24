from typing import List, Optional, Dict, Union, Literal
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import re

from models.create_location_models.model_location_pg import KeyLoc

@dataclass
class RackConfig_New:
	"""Cấu hình để generate rack locations"""
	name_rack: Union[list]
	from_bin: Union[int, list] #int là số thứ tự cần tạo bin, list là list danh sách bin dùng cho tạo những vị trí có bin không liên tục
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
	ft_prefix_chars: Optional[dict[str, str]] = field(default_factory=dict) #Dict key là name_rak, value là prefix nam_rack
	ft_prefix_at_level: Optional[dict[str, list]] = field(default_factory=dict) #Dict key là name_rack, value là list tầng cần thêm prefix_name_rack
	even_odd_both_bin: Optional[Literal['even', 'odd', 'both']] = None
	prefix_at_even_odd_bin: Optional[Literal['even', 'odd']] = None
	list_bin_ho: Optional[List[int]] = field(default_factory=list)#List vị trí cần tạo bin HO
	stack_limit: Optional[int] = 1
	is_active: Optional[Dict[int, list]] = 1 #Truyền vào 1 dict. Key là vị trí, value là tầng cần block. Giá trị mặc định là 1 (active)
	status_location: Optional[str] = "OK" #Dựa vào is_active để trả về status_location mong muốn
	note: Optional[str] = None

	def __post_init__(self):
		if isinstance(self.from_bin, int):
			if self.from_bin > self.to_bin:
				raise ValueError(f"from_bin '{self.from_bin}' lớn hơn to_bin '{self.to_bin}'")

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
	
class LocationGenerator_New:
	"""Generator để tạo locations từ config"""
	
	def __init__(self):
		self.locations_new: List[Location] = []

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
		Đối với rack dùng hệ thống mới prime thì namerack bắt đầu B01 thay vì B1.
		Vị trí là 001 thay vì 01
		Nên phải dùng regex để bắt B01 đối với rack mới và trả về vị trí 001 đổi với rack mơi.
		Rack cũ giữ nguyên logic
		"""
		# match = re.match(r"^(BT|[B]0)", name_rack) #r"(?<=[B])0
		if name_rack.startswith("HO"):
			return f"{name_rack}{rack_num:03d}"
		else:
			return f"{name_rack}{rack_num:03d}{level}"

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
	def get_rack_usage_type(name_rack: str, rack_system_type: str, ft_prefix_at_level: dict, level: str) -> str:
		"""
		Xác định type_rack đang sử dụng hiện tại 
		- Check rack_system_type = DB và len(level) = 2 -> ST.
		Đây là vị trí rack DB nhưng chuyển mục đích sử dụng sang ST 
		- Nếu name_rack là HO thì trả về HO
		- Nếu không thõa mãn thì trả về rack_system_type
		Rack mới điều kiện len(level == 2) không thõa mãn nữa.
		Đang để tạm điều kiện rack namerack B8, BT là rack đôi chuyển công năng thành rack đơn
		"""
		list_level_prefix = ft_prefix_at_level.get(name_rack, [])
		if (rack_system_type == "DB" and level in list_level_prefix):
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
			return KeyLoc.Status_Location.LOCK
		else:
			return status_location
	
	@staticmethod
	def get_footprint(pallet_capacity: int, stack_limit: int) -> int:
		"""
		Xác định footprint của location 
		footprint = papallet_capacity * stack_limitlimit
		"""
		return pallet_capacity * stack_limit
		
	def generate_from_rack_config(self, config_rack: RackConfig_New) -> List[Location]:
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
			Kiểu 3: Tạo location mới khi dùng hệ thống Prime. Location có tiền tố là "name_rack + T" (bin trong) để chuyển đổi rack đôi thành rack đơn lưu hàng lẻ, LRT
			Dựa vào 2 thuộc tính mới thêm vào của class RackConfig_New để truyền thông tin
			ft_prefix_chars = {'B08': 'BT8'},
			ft_prefix_at_level = {'B08': ['C', 'D']},
			ft_prefix_chars: Thông báo rack B08 có tiền tố BT8
			ft_prefix_at_level = {'B08': ['C', 'D']}: Thông báo tiền tố này chỉ xuất hiện ở tần C, D
			get_rack_usage_type: dựa vào ft_prefix_at_level có data không để chuyển rack_usage_type thành ST hay giữ nguyên DB
			Kiểu 4: Tạo location hệ thống mới Prime. Một bên bin là bin lẻ, bên còn lại là bin chắn
			Dựa vào thuộc tính mới thêm là: even_odd_both_bin = False mặc đinh là False
			Nếu even_odd_both_bin = True thì chuyển đổi from_bin, to_bin thành 2 list_even và list_odd sau đó nối lại và tạo location như bình thường
			Trường hợp from_bin là số chẵn thì sẽ trừ lùi 1 đơn vị để chuyển thành số lẻ.
			Mặc định location đầu tiên luôn là location lẻ
		"""
		generated_racks = []

		#Chuyển đổi form_bin, to_bin để tạo location 1 bên chẵn, 1 bên lẻ
		#Nếu from_bin được truyền vào 1 list thì trả về list truyền vào. Thường dùng tạo bin có số thứ tự không liền nhau
		#Nếu even_odd_both_bin is None thì tạo location như bình thường, số thứ tự bin tứ bé đến lớn
		#Nếu even_odd_both_bin == 'both' thì tạo bin lẻ trước, chắn sau
		#Nếu even_odd_both_bin == 'even' thì tạo chỉ bin chẵn ngược lại even_odd_both_bin == 'odd' chỉ tạo bin lẻ
		if isinstance(config_rack, RackConfig_New):
			from_bin = config_rack.from_bin
			to_bin = config_rack.to_bin
			if isinstance(from_bin, int) and from_bin != 0 and from_bin % 2 == 0:
				from_bin -= 1
			elif isinstance(from_bin, int) and from_bin == 0:
				from_bin = from_bin

			if config_rack.even_odd_both_bin == 'both':
				list_odd = list(range(from_bin, to_bin + 1, 2))
				list_even = list(range(from_bin + 1, to_bin + 1, 2))
				list_bin = list_odd + list_even
			elif config_rack.even_odd_both_bin == 'even':
				list_even = list(range(from_bin + 1, to_bin + 1, 2))
				list_bin = list_even
			elif config_rack.even_odd_both_bin == 'odd':
				list_odd = list(range(from_bin, to_bin + 1, 2))
				list_bin = list_odd
			elif isinstance(from_bin, list):
				list_bin = from_bin
			else:
				list_bin = list(range(config_rack.from_bin, config_rack.to_bin + 1))
		#Xóa bin 67 của F02, 70 của F03, F04, F05, F06 vì thực tế không có bin này
		if to_bin == 71 and config_rack.name_warehouse == 'WH2' and 70 in list_bin: list_bin.remove(70)
		if to_bin == 68 and config_rack.name_warehouse == 'WH2' and 67 in list_bin: list_bin.remove(67)
		#Vòng lặp tạo location 
		for namerack in config_rack.name_rack:
			for rack_num in list_bin:
				for str_level, num_level in config_rack.level_config.items():
					#Xác định tầng location
					level = self.get_str_level(str_level)
					#Xác định name_rack
					name_rack = self.get_name_rack(config_rack.list_bin_ho, level, rack_num, namerack)
					#Tạo location code: FA01D, B102A
					location_code = self.get_location_code(name_rack, rack_num, str_level)
					#Xác định location_system_type
					location_system_type = self.get_location_system_type(str_level)
					#Xác định location_usage_type
					location_usage_type = self.get_location_usage_type(config_rack.location_usage_type, rack_num, location_system_type)
					#Xác định rack_usage_type
					rack_usage_type = self.get_rack_usage_type(name_rack, config_rack.rack_system_type, config_rack.ft_prefix_at_level, str_level)
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
						name_rack = namerack,
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
					self.locations_new.append(location)
					#Tạo tiếp location có tiền tố BT (bin trong) nếu ft_chars_at_level có data
					if level in config_rack.ft_prefix_at_level.get(namerack, {}):
						ft_location_code = None
						#Tạo tất cả bin prefix
						if config_rack.prefix_at_even_odd_bin is None:
							prefix_location = config_rack.ft_prefix_chars.get(namerack, f"UNKNOWN {namerack}")
							ft_location_code = location_code.replace(namerack, prefix_location)
						#Chỉ tạo bin prefix có số thứ tự bin chẵn
						elif config_rack.prefix_at_even_odd_bin == "even" and rack_num % 2 == 0:
							prefix_location = config_rack.ft_prefix_chars.get(namerack, f"UNKNOWN {namerack}")
							ft_location_code = location_code.replace(namerack, prefix_location)
						#Chỉ tạo bin prefix có số thứ tự bin lẻ
						elif config_rack.prefix_at_even_odd_bin == "odd" and rack_num % 2 != 0:
							prefix_location = config_rack.ft_prefix_chars.get(namerack, f"UNKNOWN {namerack}")
							ft_location_code = location_code.replace(namerack, prefix_location)
						# Tạo location object
						# Phải check ft_location_code != None vì trong trường hợp chỉ gán prefix bên bin lẻ khi chạy đến rack_num chẵn
						#thì ft_location_code sẽ không được lọt vào điều kiện nào trong 3 điều kiện trên, nghĩa là không cần gán prefix bin chẵn
						#ft_location_code lúc đó vẫn là None sẽ không vào trong if để tạo location.
						if ft_location_code:
							location = Location(
								location = ft_location_code,
								location_system_type = location_system_type,
								location_usage_type = location_usage_type,
								rack_system_type = config_rack.rack_system_type,
								rack_usage_type = rack_usage_type,
								location_storage_type = config_rack.location_storage_type,
								zone = config_rack.zone,
								location_category = config_rack.location_category,
								location_product_category = config_rack.location_product_category,
								name_rack = namerack,
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
							self.locations_new.append(location)

		return generated_racks

	def generate_from_rack_configs(self, configs_rack: List[RackConfig_New]) -> List[Location]:
		"""Generate locations từ nhiều configs"""
		all_locations = []
		for config in configs_rack:
			locations = self.generate_from_rack_config(config)
			all_locations.extend(locations)
		return all_locations
	
	def get_all_locations(self) -> List[Location]:
		"""Lấy tất cả locations"""
		return self.locations_new

	def get_dataframe_locations(self) -> List[Dict[any, any]]:
		"""Trả về dataframe tất cả locations"""
		all_locations = []
		for loc in self.locations_new:
			all_locations.append(loc.to_dict())
		df_locations = pd.DataFrame(all_locations)
		# df_locations.to_excel("loc_system_created.xlsx", index=False)
		return df_locations

