import logging
import keyword
import operator
import re
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from models.analytics_model import AnalyticsModel

from services.chart_services import GaugeChart, Metric
from services.variable_db_container_no_usage import VariableContainer
from services.mixup_services import FindMixup
from services.emptyloc_services import EmptyLocation
from services.combinebin_services import CombineBin
#---------------
from services.vardataclass import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class DataProcessor:
	"""Lớp cơ sở để xử lý dữ liệu từ DataFrame
	"""
	_OPS_MAP = {
	'>': operator.gt, '<': operator.lt,
	'>=': operator.ge, '<=': operator.le,
	'==': operator.eq, '!=': operator.ne
	}
	def __init__(self, df_merge: Optional[pd.DataFrame]=None):
		self.df = df_merge

	def set_df_merge(self, df_merge: Optional[pd.DataFrame]=None):
		"""	Df lúc khởi tạo là empty or None
			Khi đã phân tích xong file import sẽ set df đã merge và class để phân tích
		"""
		#Sử dụng .copy(deep=True) để đảm bảo không bị ảnh hưởng tới DataFrame gốc
		self.df =df_merge.copy(deep=True)
		#Chuyển tất cả giá trị cột text về chữ thường để tránh các vấn đề về case-sensitivity
		self._normalize_data()
	
	def get_df_merge(self) ->pd.DataFrame:
		"""Trả về df đã merge nếu class khác có inject WarehoseAnalytics
		"""
		if any(self.df):
			return self.df

	def _normalize_data(self) -> None:
		"""Chuẩn hóa dữ liệu chuyển các cột text về lowrcase
		"""
		string_columns = self.df.select_dtypes(include=['object', 'string'])
		for col in string_columns:
			#Chỉ áp dụng .str.lower() cho các Series kiểu object/string
			if pd.api.types.is_string_dtype(self.df[col]):
				#Chuyển về str và xử lý NaN
				self.df[col] = self.df[col].fillna('')
				self.df[col] = self.df[col].str.lower().astype(str)
			elif isinstance(self.df[col], pd.Series): #Fallback cho các trường hợp khác có thể là object
				try:
					self.df[col] = self.df[col].fillna('')
					self.df[col] = self.df[col].astype(str).str.lower()
				except Exception:
					pass # Bỏ qua nếu không chuyển đổi được

	def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
		"""Lọc DataFrame theo các điều kiện được cung cấp
		"""
		filtered_df = self.df.copy(deep=True)
		#Tạo một mask boolean kết hợp tất cả các điều kiện
		mask = pd.Series(True, self.df.index)

		for column, values in filters.items():
			if column not in filtered_df.columns:
				logger.warning(f"Cảnh báo: Cột '{column}' không tồn tại trong DataFrame.")
				continue # Bỏ qua bộ lọc nếu cột không tồn tại
			
			if isinstance(values, (list, tuple, set)):
				mask &= filtered_df[column].isin(values)
			else:
				#So sánh trực tiếp cho giá trị đơn
				mask &= (filtered_df[column] == values)
		return filtered_df[mask].reset_index(drop=True)
	
	def _parse_expression(self, col_series, expr):
		'''
			Hàm chức năng phục vụ cho phương thức: self.fillter_other()
		'''
		# 1. Xử lý lọc Null/NaN
		if expr == 'is_null': return col_series.isna()
		if expr == 'not_null': return col_series.notna()
		
		# 2. Xử lý hàm tùy biến (Lambda)
		if callable(expr):
			try:
				return col_series.apply(expr)
			except Exception as e:
				logger.warning(f"Lỗi khi chạy hàm custom trên cột {col_series.name}: {e}")
				return pd.Series([False] * len(col_series), index=col_series.index)
		#Nếu truyền vào một số (int/float) hoặc giá trị logic (True/False), hàm sẽ so sánh bằng chính xác ngay lập tức
		if not isinstance(expr, str):
			return col_series == expr

		# 3. Xử lý toán tử so sánh & Date/Numeric (Giữ nguyên logic cũ của bạn)
		match = re.match(r'([><=!]=?)\s*(.*)', expr)
		if match:
			op_str, val_str = match.groups()
			func = self._OPS_MAP.get(op_str)
			if func:
				try:
					# Nếu là toán tử bằng hoặc khác (!=, ==) ứng với dữ liệu chuỗi (văn bản)
					if op_str in ['!=', '=='] and not 'date' in str(col_series.name).lower() and not val_str.replace('.', '', 1).isdigit():
					# Ép cả 2 về dạng chuỗi thô để so sánh chính xác, không phân biệt khoảng trắng thừa
						col_clean = col_series.astype(str).str.strip().str.lower()
						val_clean = val_str.strip().lower()
						return func(col_clean, val_clean)
					# Ép kiểu ngày tháng hoặc số
					if 'date' in str(col_series.name).lower() or "-" in val_str:
						col_eval = pd.to_datetime(col_series, errors='coerce')
						val = pd.to_datetime(val_str)
					else:
						col_eval = pd.to_numeric(col_series, errors='coerce')
						val = float(val_str)
					return func(col_eval, val).fillna(False)
				except: pass
		# 4. Tìm kiếm chuỗi nâng cao bằng Regex (Không phân biệt hoa thường)
		return col_series.astype(str).str.contains(expr, regex=True, case=False, na=False)

	def fillter_data_other(self, config: Dict[str, Any], exclude: bool = False, logic='AND') -> pd.DataFrame:
		"""
			Args: Dict có key là tên cột, value là giá trị cần fillter
			Result: Trả về DataFrame sau khi đã fillter
			Note: Có thể fillter đa chức năng như cung lấp value là list thì dùng isin
			cung cấp toán tử (><>=<=!=) sẽ tự động bóc tách toán tử và value để fillter
			cung cấp chuỗi giá trị sẽ dùng contains
			cung cấp tuple sẽ lấy giá trị từ khoảng đến khoảng...
		"""
		# Khởi tạo mask dựa trên logic AND (True) hoặc OR (False)
		if logic.upper() == 'AND':
			final_mask = pd.Series([True] * len(self.df), index=self.df.index)
		else:
			final_mask = pd.Series([False] * len(self.df), index=self.df.index)
		
		for col, criteria in config.items():
			if col not in self.df.columns:
				logger.warning(f"⚠️ Cột '{col}' không tồn tại!")
				continue
			
			# XỬ LÝ TRƯỜNG HỢP: Điều kiện là một Danh sách (List)
			if isinstance(criteria, list) and len(criteria) > 0:
				# Kiểm tra phần tử đầu tiên xem có bắt đầu bằng toán tử so sánh (như !=, >, <) hay không
				first_item = str(criteria[0]).strip()
				has_operator = any(first_item.startswith(op) for op in self._OPS_MAP.keys())
				
				if has_operator:
					# TRƯỜNG HỢP A: List chứa toán tử (Ví dụ: ['!= rej', '!= lsl']) -> Kết hợp bằng toán tử AND (&)
					mask = pd.Series([True] * len(self.df), index=self.df.index)
					for single_expr in criteria:
						mask = mask & self._parse_expression(self.df[col], single_expr)
				else:
					# TRƯỜNG HỢP B: List thuần túy (Ví dụ: ['rej', 'lsl']) -> Dùng .isin() tìm chính xác
					# Làm sạch dữ liệu để tránh lỗi lệch chữ hoa/thường hoặc khoảng trắng thừa
					col_clean = self.df[col].astype(str).str.strip().str.lower()
					list_clean = [str(x).strip().lower() for x in criteria]
					mask = col_clean.isin(list_clean)
			# XỬ LÝ TRƯỜNG HỢP: Điều kiện là một Danh sách (Tuple). Tìm kiếm trong một khoảng
			elif isinstance(criteria, tuple):
				mask = self.df[col].between(*criteria)
			else:
				mask = self._parse_expression(self.df[col], criteria)
			
			# Kết hợp mask theo logic mong muốn
			if logic.upper() == 'AND':
				final_mask &= mask
			else:
				final_mask |= mask

		actual_mask = ~final_mask if exclude else final_mask
		self.dropped_data = self.df[~actual_mask].copy()

		return self.df[actual_mask]

@dataclass
class WarehouseFilter:
	"""Lớp chứa các thông tin về bộ lọc cho mỗi kho hàng
	"""
	name_warehouse: List[str]
	location_usage_type: List[str]
	cat_inv: List[str] = field(default_factory=lambda: ["eo", 'fg', 'rpm'])

	def get_filter_dict(self) -> Dict[str, List[str]]:
		"""Trả về bộ lọc dưới dạng dictionary
		"""
		return {
			"name_warehouse": self.name_warehouse,
			"location_usage_type": self.location_usage_type,
			"cat_inv": self.cat_inv
		}
	
class WarehouseAnalyzer(DataProcessor):
	"""
	Lớp phân tích dữ liệu kho hàng và tính toán số pallet theo các tiêu chí
	"""
	def __init__(self, analytics_model: AnalyticsModel, df_merge: Optional[pd.DataFrame]=None):
		super().__init__(df_merge)
		self.analytics_model = analytics_model
		
		self._setup_warehouse_filters()
		self._setup_other_location_fillter()
		
		#Khởi tạo các biến cần phải check để chạy lấy df, từ đó lấy được số pallet để đưa lên dashboard
		#Mục đích để chạy hàm tổng hợp 1 lần tránh phải chạy 2 lần khi chương trình được chạy
		self.df_mixup = pd.DataFrame()
		self.df_empty_loc = pd.DataFrame()
		self.df_combinebin = pd.DataFrame()

	def _setup_warehouse_filters(self) -> None:
		"""
		Thiết lập các bộ lọc cho các kho hàng khác nhau
		"""
		self.warehouse_filters = {
			"wh1": WarehouseFilter(
				name_warehouse=["wh1"],
				location_usage_type=["hr", "pf", "ww", "in"]
			),
			"wh2": WarehouseFilter(
				name_warehouse=["wh2"],
				location_usage_type=["hr", "pf", "ww", "in", "pick", "rework", "return", "scanout"]
			),
			"wh3": WarehouseFilter(
				name_warehouse=["wh3"],
				location_usage_type=["hr", "pf", "ww", "in"]
			),
			"lsl": WarehouseFilter(
				name_warehouse=["lsl"],
				location_usage_type=["in", "lslpm", "lslrm", "lrt"]
			),
			"lb": WarehouseFilter(
				name_warehouse=["lb"],
				location_usage_type=["hr", "pf", "ww"]
			),
			"cool": WarehouseFilter(
				name_warehouse=["cool1", "cool2", "cool3"],
				location_usage_type=["mk", "ww"]
			),
			"pf": WarehouseFilter(
				name_warehouse=["pf1", "pf2", "pf3", "pf4", "pf5"],
				location_usage_type=["mk", "ww"]
			),
			 "steam": WarehouseFilter(
				name_warehouse=["steam"], # Giả định 'rej' là tên kho cho loại 'steam'
				location_usage_type=["reject"]
			)
			# Có thể thêm các cấu hình kho khác tại đây
		}

	def analyze_warehouse(self, warehouse_key: str) -> Dict[str, float]:
		"""
		Phân tích một kho hàng cụ thể và trả về kết quả chi tiết theo tổ hợp name_warehouse_location_usage_type_cat_inv.
		"""
		if warehouse_key not in self.warehouse_filters:
			#Trả về dictionary rỗng thay vì raise lỗi để get_comprohensive_analysis không bị dừng
			logger.warning(f"Cảnh báo: Không có cấu hình kho hàng: {warehouse_key}. Bỏ qua.")
			return {}
		#Lấy bộ lọc theo từng kho
		wh_filter = self.warehouse_filters[warehouse_key]
		filter_dict = wh_filter.get_filter_dict()

		results = {}
		#Lọc data theo bộ lọc chung của nhóm kho (name_warehouse, location_usage_type, cat_inv)
		# {'name_warehouse': ['wh2'], 'location_usage_type': ['hr', 'pf', 'ww', 'in', 'pick', 'rework', 'return', 'scanout'], 'cat_inv': ['eo', 'fg', 'rpm']}
		#['pf1', 'pf2', 'pf3', 'pf4', 'pf5'], 'location_usage_type': ['mk', 'ww'], 'cat_inv': ['eo', 'fg', 'rpm']}
		group_filtered_df = self.filter_data(filter_dict)

		#Tính toán kết quả cho mỗi name_warehouse, location_usage_type và cat_inv CÓ TRONG DỮ LIỆU ĐÃ LỌC
		# Duyệt qua các giá trị name_warehouse, location_usage_type, cat_inv CÓ TRONG group_filter_df
		#để tránh tạo ra các key cho tổ hợp không tồn tại
		actual_name_warehouses = group_filtered_df["name_warehouse"].unique()
		# actual_location_usage_types = group_filtered_df["location_usage_type"].unique()
		# actual_cat_invs = group_filtered_df["cat_inv"].unique()

		for wh in wh_filter.name_warehouse:
			if wh not in actual_name_warehouses: continue # Chỉ xử lý nếu kho này có trong dữ liệu đã lọc

			wh_df = group_filtered_df[group_filtered_df["name_warehouse"] == wh]
			actual_wh_location_usage_types = wh_df["location_usage_type"].unique()

			for location_usage_type in wh_filter.location_usage_type:
				if location_usage_type not in actual_wh_location_usage_types: continue # Chỉ xử lý nếu loại kệ này có trong dữ liệu của kho đang xét

				location_usage_type_df = wh_df[wh_df["location_usage_type"] == location_usage_type]
				actual_wh_location_usage_type_cat_invs = location_usage_type_df['cat_inv'].unique()

				for cat_inv in wh_filter.cat_inv:
					if cat_inv not in actual_wh_location_usage_type_cat_invs: continue # Chỉ xử lý nếu danh mục này có trong dữ liệu của tổ hợp đang xét

					sub_df = location_usage_type_df[location_usage_type_df["cat_inv"] == cat_inv]
					result_key = f"{wh}_{location_usage_type}_{cat_inv}"
					results[result_key] = sub_df["pallet"].sum() if not sub_df.empty else 0
		
		return results
	
	def analyze_all_warehouses(self) -> Dict[str, Dict[str, float]]:
		"""
		Phân tích tất cả các nhóm kho được cấu hình và trả về kết quả gộp
		"""
		raw_all_results: Dict[str, float] = {}
		for wh_key in self.warehouse_filters.keys():
			# Sử dụng update để gộp kết quả từ analyze_warehouse vào all_results
			# keys từ analyze_warehouse đã có dạng wh_type_cat
			raw_all_results.update(self.analyze_warehouse(wh_key))
		#THÊM các vị trí cấu hình nhưng không có data (gán 0), và lưu vào all_results.
		potential_wh_type_cat_keys = self.get_all_potential_wh_type_cat_keys()
		final_results: Dict[str, float] = {key: 0 for key in potential_wh_type_cat_keys}
		# Cập nhật/Thêm các key từ kết quả thô
		final_results.update(raw_all_results)
		
		return final_results
	
	def _setup_other_location_fillter(self) ->None:
		'''
			Thiết lập bộ lọc cho các vị trí đặc biệt, không theo quy luật
			
		'''
		self.other_location_fillters = {
			'block': {
				'status': ['hd'],
				'name_warehouse': ['!=steam', '!=lsl'],
			},
			'special': {
				'location': ['fgls', 'fgdm', 'matdm', 'lost']
			},
			'fg_other': {
				'cat_inv': ['fg'],
				'name_warehouse': ['!=steam', '!=lsl'],
				'cat': ['dwn', 'febz', 'hdl']
			},
			'jit': {
				'cat_inv': ['rpm'],
				'name_warehouse': ['!=steam', '!=lsl'],
				'jit': ['jit']
			},
			'pm_other': {
				'cat_inv': ['rpm'],
				'name_warehouse': ['!=steam', '!=lsl'],
				'type2': ['shipper', 'pouch', 'bottle']
			},
			'da': {
				'rack_usage_type': ['ob'],
			},
			'sv': {
				'rack_usage_type': ['sv'],
				'name_warehouse': ['wh3']
			},
			'ho': {
				'rack_usage_type': ['ho'],
			},
			'fg': {
				'cat_inv': ['fg'],
				'name_warehouse': ['wh1', 'wh2', 'wh3', 'nan', '']
			},
			'pm': {
				'cat_inv': ['rpm'],
				'type1': ['!=raw_mat'],
				'name_warehouse': ['wh1', 'wh2', 'wh3', 'nan', '']
			},
			'rm': {
				'cat_inv': ['rpm'],
				'type1': ['raw_mat'],
				'name_warehouse': ['wh1', 'wh2', 'wh3', 'nan', '']
			},
			'eo': {
				'cat_inv': ['eo'],
				'name_warehouse': ['wh1', 'wh2', 'wh3', 'lsl', 'nan', '']
			}
		}
		#========================================================================
		self.other_location_fillters_layer_2 = {
			'block': {
				'cat_inv': ['fg', 'rpm', 'eo'],
				'name_warehouse': ['lb'],
				'type1': ['raw_mat']
			},
			'special': {
				'location': ['fgls', 'fgdm', 'matdm', 'lost']
				},
			'fg_other': {
				'cat': ['dwn', 'febz', 'hdl']
			},
			'jit': {
				'jit': ['jit'],
			},
			'pm_other': {
				'type2': ['shipper', 'pouch', 'bottle']
			},
			'da': {
				'location_usage_type': ['pf', 'hr'],
				'cat_inv': ['fg', 'rpm', 'eo']
			},
			'sv': {
				'location_usage_type': ['pf', 'hr'],
				'cat_inv': ['fg', 'rpm', 'eo']
			},
			'ho': {
				'location_usage_type': ['pf', 'hr'],
				'cat_inv': ['fg', 'rpm', 'eo']
			},
			'fg': {
				'cat_inv': ['fg']
			},
			'pm': {
				'cat_inv': ['rpm']
			},
			'rm': {
				'cat_inv': ['rpm']
			},
			'eo': {
				'cat_inv': ['eo']
			}
		}

	def analyze_all_other_location(self) -> Dict[str, Any]:
		'''
			No comment
		'''
		other_all_results: Dict[str, float] = {}
		for key, config in self.other_location_fillters.items():
			result = self.fillter_data_other(config)
			dict_fillter_layer_2 = self.other_location_fillters_layer_2.get(key, {})
			special_keys = {'location_usage_type', 'cat_inv'}
			if special_keys.issubset(dict_fillter_layer_2.keys()):
				# TỐI ƯU: Chuẩn hóa 2 cột này trước 1 lần duy nhất ngoài vòng lặp
				res_loc_clean = result['location_usage_type'].str.strip().str.lower()
				res_cat_clean = result['cat_inv'].str.strip().str.lower()
				
				type_values = dict_fillter_layer_2['location_usage_type']
				cat_values = dict_fillter_layer_2['cat_inv']
				for type_loc in type_values:
					loc_lower = type_loc.lower()
					# Lọc theo location_usage_type
					df_type = result[res_loc_clean == loc_lower]
					
					# Cắt bớt phần series đã lọc tương ứng để dùng cho vòng lặp trong
					res_cat_sub = res_cat_clean[res_loc_clean == loc_lower]
					for cat in cat_values:
						cat_lower = cat.lower()
						df_type_cat = df_type[res_cat_sub == cat_lower]
						
						key_count = f"{key}_{type_loc}_{cat}"
						other_all_results[key_count] = df_type_cat['pallet'].sum().item() if not df_type_cat.empty else 0
			else:
				for col, values in dict_fillter_layer_2.items():
					# TỐI ƯU: Chuẩn hóa cột hiện tại 1 lần trước khi lặp qua danh sách `values`
					res_col_clean = result[col].str.strip().str.lower()
					for k in values:
						df_result_layer_2 = result[res_col_clean == k.lower()]
						key_count = f"{key}_{k}"
						other_all_results[key_count] = df_result_layer_2['pallet'].sum().item() if not df_result_layer_2.empty else 0
				
			# print(f"Số dòng tìm kiếm được {key}: {len(result)}. Tổng số pallet: {result['pallet'].sum()}")
			# print(result[['gcas', 'batch', 'status', 'qty', 'pallet', 'location', 'cat_inv']])
		return other_all_results

	def get_mixup(self) -> pd.DataFrame:
		"""Lấy bin mixup 
		"""
		if self.df_mixup.empty:
			self.df_mixup = FindMixup(self.df).get_mixup()
			return self.df_mixup
		else:
			return self.df_mixup
	
	def count_location_mixup(self) -> int:
		"""Lấy số lượng bin mixup đưa lên dashboard sau khi đã lấy df_mixup
		"""
		df_mixup = self.get_mixup()
		result = {}
		location_mixup = df_mixup['location'].nunique() if not df_mixup.empty else 0
		result['pallet_mixup'] = location_mixup

		return result

	def get_empty_location(self) -> pd.DataFrame:
		"""Lấy vị trí trong theo data frame hiện tại.
			Args:
				dataframe masterlocion lấy từ analytics_controller
		"""
		if self.df_empty_loc.empty:
			df_masterloc = self.analytics_model.get_master_location()
			self.df_empty_loc = EmptyLocation(df_data=self.df, df_masterloc=df_masterloc).get_empty_location()
			return self.df_empty_loc
		else:
			return self.df_empty_loc
	
	def count_pallet_bin_empty(self) -> int:
		"""Lấy số pallet còn trống trong wh1, wh2, wh2
		"""
		df = self.get_empty_location()
		df['pallet_capacity'] = pd.to_numeric(df['pallet_capacity'], downcast='integer')
		mask = pd.Series(True, df.index)
		mask &= df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
		df_empty_loc = df[mask]
		pallet_emptybin = df_empty_loc['pallet_capacity'].sum() if not df_empty_loc.empty else 0

		result = {}
		result['pallet_emptybin'] = pallet_emptybin
		
		return result

	
	def get_combinebin(self) -> pd.DataFrame:
		"""	Lấy những vị trí đang tồn 1 pallet ở trên bin.
			Tìm những bin có cùng gcas và lot đang ở bin đôi và đang có tồn 1 pallet.
			Mục đích giải phóng bin có tồn 1 pallet và tối ưu bin double để full 2 pallet.
		"""
		if self.df_combinebin.empty:
			self.df_combinebin = CombineBin(self.df).get_combinebin()
			return self.df_combinebin
		else:
			return self.df_combinebin
	
	def count_bin_combine(self) -> int:
		"""Get pallet cần combine bin
		"""
		df_combinebin = self.get_combinebin()
		results = {}
		location_combinebin = len(df_combinebin) if not df_combinebin.empty else 0
		results['pallet_combinebin'] = location_combinebin

		return results
	
	def get_all_potential_wh_type_cat_keys(self) -> List[str]:
		"""
		Tạo ra danh sách TẤT CẢ các key wh_type_cat có thể có dựa trên cấu hình filter,
		bất kể dữ liệu thực tế có tồn tại hay không.
		Hữu ích cho việc định nghĩa cấu trúc hiển thị trên dashboard.
		"""
		potential_keys = set()
		for wh_key, wh_filter in self.warehouse_filters.items():
			for wh in wh_filter.name_warehouse:
				for location_usage_type in wh_filter.location_usage_type:
					for cat_inv in wh_filter.cat_inv:
						potential_keys.add(f"{wh}_{location_usage_type}_{cat_inv}")

		# Chuyển set sang list và sắp xếp để kết quả luôn nhất quán
		return sorted(list(potential_keys), reverse=True)
	
	def get_comprehensive_analysis(self) -> Dict[str, float]:
		"""
		Lấy tất cả kết quả phân tích và kết hợp thành một dictionary duy nhất.
		"""
		results: Dict[str, float] = {}
		
		#Phân tích từng nhóm kho
		warehouse_results = self.analyze_all_warehouses()
		results.update(warehouse_results)
		#Phân tích các vị trí đặc biệt
		other_location_result = self.analyze_all_other_location()
		results.update(other_location_result)
		#Count location mixup
		location_mixup = self.count_location_mixup()
		results.update(location_mixup)

		#Count bin cần combine
		pallet_combinebin = self.count_bin_combine()
		results.update(pallet_combinebin)

		#Count bin empty
		pallet_emptybin = self.count_pallet_bin_empty()
		results.update(pallet_emptybin)

		return results
	
	def get_chart_for_dashboard(self):
		"""Từ Dict name_warehouse_location_usage_type_cat_inv biến đổi thành name_warehouse_location_usage_type.
			Đưa gọi chart trả về obj để view lên dashboard
		"""
		#Get Dict sau khi tổng hợp từ config warehouse
		dict_namewh_typerack_catinv: Dict[str, float] = self.get_comprehensive_analysis()
		container = VarContainerDrivative(**dict_namewh_typerack_catinv)
		chart_config = ChartConfig(container)
		obj_all_chart = chart_config.render_chart()

		return obj_all_chart

		
class VariableChartContainer:
	def __init__(self, variables_dict: Dict[str, Any]):
		"""
		Khởi tạo đối tượng từ một dictionary.

		Args:
			variables_dict (dict): Dictionary có key là tên biến (string)
								và value là giá trị obj.
		"""
		if not isinstance(variables_dict, dict):
			logger.error(f"Đầu vào phải là một dictionary.")
			raise
		
		for key, value in variables_dict.items():
			# Kiểm tra xem key có phải là tên thuộc tính (biến) hợp lệ trong Python không
			# isidentifier() kiểm tra cú pháp tên biến
			# keyword.iskeyword() kiểm tra xem tên có phải là từ khóa reserved không
			if isinstance(key, str) and key.isidentifier() and not keyword.iskeyword(key):
				setattr(self, key, value)
				# logger.info(f"Đã gán: self.{key} = {value}") # Có thể bỏ comment để debug
			else:
				logger.warning(f"Cảnh báo: Key '{key}' không phải là tên biến hợp lệ. Bỏ qua.")

	def to_dict(self):
		return self.__dict__

'''
Block:
Tính tổng pallet có status HD và trừ vị trí stream có name_warehouse là STEAM và EOL có name_warehouse LSL
Tính riêng pallet block của fg, rpm, lable và rm
Trong pallet block_rpm vẫn có block_rm. Block_rm tính riêng ra đề trừ đi số pallet NORM. RM
Tổng pallet Block sẽ được tính trong VariableContainer
FG_with_cat
Count Pallet theo Cat dwn, febz, hdl dựa vào cat_inv là FG và cột cat (masterdata)
Không lấy pallet ở steam và lsl có name_warehouse lần lượt là rej, lsl
Pallet FG_Other sẽ được tính trong VariableContainer. Lấy tổng FG trừ 3 cái còn lại
JIT
Không lấy pallet ở steam và lsl có name_warehouse lần lượt là rej, lsl
Lấy tổng pallet ở cột jit có nội dung là jit và cat_inv là rpm
RPM_with_type2
Không lấy pallet ở steam và lsl có name_warehouse lần lượt là rej, lsl
Cout pallet theo cat_inv và type2 shipper, pouch, bottle.
Muốn tính được other phải lấy tổng trừ đi 3 cái còn lại
Rack DA
Count pallet có cột rack_usage_type là ob
Rack HO
Cout pallet có cột rack_usage_type là ho
Total_FG
Count tất cả pallet có cat_inv là FG.
Tránh trường hợp count sót khi gcas chưa có trong masterdata
Chỉ count những vị trí có trong 'wh1', 'wh2', 'wh3'
Total_PM
Tính tổng cột pallet có cat_inv là rpm.
Không lấy pallet ở steam và lsl có name_warehouse lần lượt là rej, lsl, label.
Sở dĩ không lọc trong wh1,2,3 vì có trường hợp pm sẽ đem vào lưu cooling3, cooling1 trong những ngày kho đầy
Cột type1 khác raw_mat
Toal_RM
Tính tổng cột pallet có cat_inv là rpm.
Chỉ lấy trong wh1,2,3 và những dòng trống vì location chưa update trong masterlocation
Sở dĩ không lấy như pm là loại những pallet ở steam, lsl, label vì hàng rm khi lưu vào các
kho đặc biệt như cool1,2,3 or pf1,2,3,4,5 đã được count riêng rồi.
Cột type1 bằng raw_mat
Total_EO
Tính tổng cột pallet có cat_inv là EO
'''
'''
	cũ trước khi chuyển sang dataclass: def get_chart_for_dashboard(self):
	#===================================================
		#Set đối tượng cho từng items của dict. Key làm tên biến, value làm value của biến
		# dict_data_draw_chart = VariableContainer(dict_namewh_typerack_catinv).get_comprehensive_data_chart()
		# dict_all_chart: Dict[str, Any] = {}
		# for name, pallet_type in dict_data_draw_chart.items():
		# 	if pallet_type.type_chart == 1:
		# 		fig = GaugeChart(pallet_type.title_chart, pallet_type.pallet, pallet_type.capa_chart, pallet_type.height_chart).create_fig()
		# 		dict_all_chart[name] = fig
		# 	elif  pallet_type.type_chart == 2:
		# 		fig = Metric(pallet_type.title_chart, pallet_type.pallet).create_metric_card()
		# 		dict_all_chart[name] = fig
		# 	elif  pallet_type.type_chart == 3:
		# 		dict_all_chart[name] = pallet_type.cu_chart
				
		# obj_all_chart = VariableChartContainer(dict_all_chart)
	#=====================================================
'''