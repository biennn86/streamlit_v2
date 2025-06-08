import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
from services.chart_services import GaugeChart, Metric
from services.support_sevices import VariableContainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class DataProcessor:
	"""Lớp cơ sở để xử lý dữ liệu từ DataFrame
	"""
	def __init__(self, df: Optional[pd.DataFrame]=None):
		if isinstance(df, pd.DataFrame):
			#Sử dụng .copy(deep=True) để đảm bảo không bị ảnh hưởng tới DataFrame gốc
			self.df =df.copy(deep=True)
			#Chuyển tất cả giá trị cột text về chữ thường để tránh các vấn đề về case-sensitivity
			self._normalize_data()
	
	def _normalize_data(self) -> None:
		"""Chuẩn hóa dữ liệu chuyển các cột text về lowrcase
		"""
		string_columns = self.df.select_dtypes(include=['object', 'string'])
		for col in string_columns:
			#Chỉ áp dụng .str.lower() cho các Series kiểu object/string
			if pd.api.types.is_string_dtype(self.df[col]):
				#Chuyển về str và xử lý NaN
				self.df[col] = self.df[col].str.lower().astype(str).fillna('')
			elif isinstance(self.df[col], pd.Series): #Fallback cho các trường hợp khác có thể là object
				try:
					self.df[col] = self.df[col].astype(str).str.lower().fillna('')
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

@dataclass
class WarehouseFilter:
	"""Lớp chứa các thông tin về bộ lọc cho mỗi kho hàng
	"""
	name_wh: List[str]
	type_rack: List[str]
	cat_inv: List[str] = field(default_factory=lambda: ["eo", 'fg', 'rpm'])

	def get_filter_dict(self) -> Dict[str, List[str]]:
		"""Trả về bộ lọc dưới dạng dictionary
		"""
		return {
			"name_wh": self.name_wh,
			"type_rack": self.type_rack,
			"cat_inv": self.cat_inv
		}
	
@dataclass
class DynamicWarehouseFilter:
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)
	
	def get_dynamic_filter_dict(self):
		return self.__dict__
	
class WarehouseAnalyzer(DataProcessor):
	"""
	Lớp phân tích dữ liệu kho hàng và tính toán số pallet theo các tiêu chí
	"""
	def __init__(self, df: Optional[pd.DataFrame]=None):
		super().__init__(df)
		self._setup_warehouse_filters()

	def _setup_warehouse_filters(self) -> None:
		"""
		Thiết lập các bộ lọc cho các kho hàng khác nhau
		"""
		self.warehouse_filters = {
			"wh1": WarehouseFilter(
				name_wh=["wh1"],
				type_rack=["hr", "pf", "ww", "in"]
			),
			"wh2": WarehouseFilter(
				name_wh=["wh2"],
				type_rack=["hr", "pf", "ww", "in", "pick", "rework", "return", "scanout"]
			),
			"wh3": WarehouseFilter(
				name_wh=["wh3"],
				type_rack=["hr", "pf", "ww", "in"]
			),
			"lsl": WarehouseFilter(
				name_wh=["lsl"],
				type_rack=["in", "lslpm", "lslrm", "lrt"]
			),
			"lb": WarehouseFilter(
				name_wh=["lb"],
				type_rack=["hr", "pf", "ww"]
			),
			"cool": WarehouseFilter(
				name_wh=["cool1", "cool2", "cool3"],
				type_rack=["mk", "ww"]
			),
			"pf": WarehouseFilter(
				name_wh=["pf1", "pf2", "pf3", "pf4", "pf5"],
				type_rack=["mk", "ww"]
			),
			 "steam": WarehouseFilter(
				name_wh=["rej"], # Giả định 'rej' là tên kho cho loại 'steam'
				type_rack=["reject"]
			)
			# Có thể thêm các cấu hình kho khác tại đây
		}

	def analyze_warehouse(self, warehouse_key: str) -> Dict[str, float]:
		"""
		Phân tích một kho hàng cụ thể và trả về kết quả chi tiết theo tổ hợp name_wh_type_rack_cat_inv.
		"""
		if warehouse_key not in self.warehouse_filters:
			#Trả về dictionary rỗng thay vì raise lỗi để get_comprohensive_analysis không bị dừng
			logger.warning(f"Cảnh báo: Không có cấu hình kho hàng: {warehouse_key}. Bỏ qua.")
			return {}
		wh_filter = self.warehouse_filters[warehouse_key]
		filter_dict = wh_filter.get_filter_dict()

		results = {}
		#Lọc data theo bộ lọc chung của nhóm kho (name_wh, type_rack, cat_inv)
		group_filtered_df = self.filter_data(filter_dict)

		#Tính toán kết quả cho mỗi name_wh, type_rack và cat_inv CÓ TRONG DỮ LIỆU ĐÃ LỌC
		# Duyệt qua các giá trị name_wh, type_rack, cat_inv CÓ TRONG group_filter_df
		#để tránh tạo ra các key cho tổ hợp không tồn tại
		actual_name_whs = group_filtered_df['name_wh'].unique()
		actual_type_racks = group_filtered_df['type_rack'].unique()
		actual_cat_invs = group_filtered_df['cat_inv'].unique()

		for wh in wh_filter.name_wh:
			if wh not in actual_name_whs: continue # Chỉ xử lý nếu kho này có trong dữ liệu đã lọc

			wh_df = group_filtered_df[group_filtered_df["name_wh"] == wh]
			actual_wh_type_racks = wh_df['type_rack'].unique()

			for type_rack in wh_filter.type_rack:
				if type_rack not in actual_wh_type_racks: continue # Chỉ xử lý nếu loại kệ này có trong dữ liệu của kho đang xét

				type_rack_df = wh_df[wh_df["type_rack"] == type_rack]
				actual_wh_type_rack_cat_invs = type_rack_df['cat_inv'].unique()

				for cat_inv in wh_filter.cat_inv:
					if cat_inv not in actual_wh_type_rack_cat_invs: continue # Chỉ xử lý nếu danh mục này có trong dữ liệu của tổ hợp đang xét

					sub_df = type_rack_df[type_rack_df["cat_inv"] == cat_inv]
					result_key = f"{wh}_{type_rack}_{cat_inv}"
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
	
	def count_block_pallet(self) -> Dict[str, float]:
		"""
			Tính tổng pallet có status HD và trừ vị trí stream có name_wh là REJ và EOL có name_wh LSL
			Tính riêng pallet block của fg, rpm, lable và rm
			Trong pallet block_rpm vẫn có block_rm. Block_rm tính riêng ra đề trừ đi số pallet NORM. RM
			Tổng pallet Block sẽ được tính trong VariableContainer
		"""
		if "status" not in self.df.columns:
			logger.warning(f"Cột 'status' không tồn tại. Không thể tính pallet bị khóa.")
			return {}
		#Tạo bộ lọc
		filtered_df = self.df[self.df['status'] == "hd"].copy()
		mask = pd.Series(True, filtered_df.index)
		mask = (filtered_df['name_wh'] != 'rej')&(filtered_df['name_wh'] != 'lsl')
		filtered_df = filtered_df[mask]

		results = {}

		#Tính pallet fg, eo block
		for cat_inv in ['fg', 'eo', 'rpm']:
			sub_df = filtered_df[filtered_df['cat_inv'] == cat_inv]
			result_key = f"block_{cat_inv}"
			results[result_key] = sub_df['pallet'].sum() if not sub_df.empty else 0

		#Tính pallet block raw_mat và label
		block_rm_df = filtered_df[filtered_df['type1'] == 'raw_mat']
		block_lb_df = filtered_df[filtered_df['name_wh'] == 'lb']
		results['block_rm'] = block_rm_df['pallet'].sum() if not block_rm_df.empty else 0
		results['block_lb'] = block_lb_df['pallet'].sum() if not block_lb_df.empty else 0

		#Tính lại pallet block_rpm. Lấy block_rpm - block_lb
		results['block_rpm'] = results['block_rpm'] - results['block_lb']
		
		return results
	
	def count_pallet_fgls_fgdm_matdm_lost(self) -> Dict[str, float]:
		"""Tính tổng pallet có trong 4 vị trí trên
		"""
		if "location" not in self.df.columns:
			logger.warning(f"Cột 'location' không tồn tại. Không thể tính pallet các vị trí FGLS, FGDM, MATDM, LOST.")
			return {}
		
		filtered_df = self.df[self.df['location'].isin(['fgls', 'fgdm', 'matdm', 'lost'])].copy()

		results = {}

		for loc in ['fgls', 'fgdm', 'matdm', 'lost']:
			sub_df = filtered_df[filtered_df['location'] == loc]
			key_result = f"pallet_{loc}"
			results[key_result] = sub_df['pallet'].sum() if not sub_df.empty else 0
		
		return results
	
	def count_pallet_fg_with_cat(self) -> Dict[str, float]:
		"""Count Pallet theo Cat dwn, febz, hdl dựa vào cat_inv là FG và cột cat (masterdata)
		Trừ đi hàng ở steam và lsl
		Pallet FG_Other sẽ được tính trong VariableContainer
		"""
		if "cat" not in self.df.columns:
			logger.warning(f"Cột 'cat' không tồn tại. Không thể tính pallet theo CAT.")
			return {}
		
		mask = pd.Series(True, self.df.index)
		mask &= (self.df['name_wh'] != 'rej')&(self.df['name_wh'] != 'lsl')
		mask &= self.df['cat_inv'] == 'fg'
		mask &= self.df['cat'].isin(['dwn', 'febz', 'hdl'])

		filtered_df = self.df[mask].copy()

		results = {}

		for cat in ['dwn', 'febz', 'hdl']:
			sub_df = filtered_df[filtered_df['cat'] == cat]
			key_result = f"pallet_fg{cat}"
			results[key_result] = sub_df['pallet'].sum() if not sub_df.empty else 0

		return results





	def get_all_potential_wh_type_cat_keys(self) -> List[str]:
		"""
		Tạo ra danh sách TẤT CẢ các key wh_type_cat có thể có dựa trên cấu hình filter,
		bất kể dữ liệu thực tế có tồn tại hay không.
		Hữu ích cho việc định nghĩa cấu trúc hiển thị trên dashboard.
		"""
		potential_keys = set()
		for wh_key, wh_filter in self.warehouse_filters.items():
			for wh in wh_filter.name_wh:
				for type_rack in wh_filter.type_rack:
					for cat_inv in wh_filter.cat_inv:
						potential_keys.add(f"{wh}_{type_rack}_{cat_inv}")

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

		# Count pallet block
		block_pallet = self.count_block_pallet()
		results.update(block_pallet)
		
		#Count pallet FGLS, FGDM, MATDM, LOST
		pallet_fgls_fgdm_matdm_lost = self.count_pallet_fgls_fgdm_matdm_lost()
		results.update(pallet_fgls_fgdm_matdm_lost)

		#Count pallet FG with CAT
		pallet_fg_with_cat = self.count_pallet_fg_with_cat()
		results.update(pallet_fg_with_cat)


		return results
	
	

	
	def get_chart_for_dashboard(self):
		"""Từ Dict name_wh_type_rack_cat_inv biến đổi thành name_wh_type_rack.
			Đưa gọi chart trả về obj để view lên dashboard
		"""
		#Get Dict sau khi tổng hợp từ config warehouse
		dict_namewh_typerack_catinv: Dict[str, float] = self.get_comprehensive_analysis()
		#Set đối tượng cho từng items của dict. Key làm tên biến, value làm value của biến
		dict_data_draw_chart = VariableContainer(dict_namewh_typerack_catinv).get_comprehensive_data_chart()

		dict_all_chart: Dict[str, Any] = {}
		for name, pallet_type in dict_data_draw_chart.items():
			if pallet_type.type_chart == 1:
				fig = GaugeChart("", pallet_type.pallet, pallet_type.capa_chart).create_fig()
				dict_all_chart[name] = fig
			else:
				fig = Metric("unknown", pallet_type.pallet).get_info_metric()
				dict_all_chart[name] = fig
		return dict_all_chart
				
		
		#Tạo dict chứa key, value và type chart của từng vị trí
		# dict_namewh_typerack_typechart: Dict[str, Dict[float, float]] = {}
		# total_for_group = 0
		# for key, value in dict_groupby.items():
		# 	if key.startswith(f"wh1"):
		# 		total_for_group += value
		# 		dict_namewh_typerack_typechart[key] = {value, 1}
		# 		dict_namewh_typerack_typechart['total_wh1'] = {total_for_group, 1}


		# print(dict_namewh_typerack_typechart)



		# dothi = CreateGauge("", variable_raw.wh1_hr, 4800).create_fig()
		# metric = Metric(label="Kho 2", value=variable_raw.wh1_pf).get_info_metric()
		# return dothi, metric

