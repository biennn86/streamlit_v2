import logging
import keyword
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np

from models.analytics import AnalyticsModel

from services.chart_services import GaugeChart, Metric
from services.variable_db_container import VariableContainer
from services.mixup_services import FindMixup
from services.emptyloc_services import EmptyLocation
from services.combinebin_services import CombineBin


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class DataProcessor:
	"""Lớp cơ sở để xử lý dữ liệu từ DataFrame
	"""
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
	
class WarehouseAnalyzer(DataProcessor):
	"""
	Lớp phân tích dữ liệu kho hàng và tính toán số pallet theo các tiêu chí
	"""
	def __init__(self, analytics_model: AnalyticsModel, df_merge: Optional[pd.DataFrame]=None):
		super().__init__(df_merge)
		self.analytics_model = analytics_model
		
		self._setup_warehouse_filters()
		
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
		df['num_pallet'] = pd.to_numeric(df['num_pallet'], downcast='integer')
		mask = pd.Series(True, df.index)
		mask &= df['name_wh'].isin(['wh1', 'wh2', 'wh3'])
		df_empty_loc = df[mask]
		pallet_emptybin = df_empty_loc['num_pallet'].sum() if not df_empty_loc.empty else 0

		result = {}
		result['pallet_emptybin'] = pallet_emptybin
		
		return result

	
	def get_combinebin(self) -> pd.DataFrame:
		"""	Lấy những vị trí đang tồn 1 pallet ở trên bin.
			Tìm những bin có cùng gcas và lot đang ở bin đôi và đang có tồn 1 pallet.
			Mục đích giải phóng bin có tồn 1 pallet và tối ưu bin double để full 2 pallet.
		"""
		if self.df_combinebin.empty:
			df_combinebin = CombineBin(self.df).get_combinebin()
			return df_combinebin
		else:
			return df_combinebin
	
	def count_bin_combine(self) -> int:
		"""Get pallet cần combine bin
		"""
		df_combinebin = self.get_combinebin()
		results = {}
		location_combinebin = len(df_combinebin) if not df_combinebin.empty else 0
		results['pallet_combinebin'] = location_combinebin

		return results
	
	
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
			result_key = f"block_pl{cat_inv}"
			results[result_key] = sub_df['pallet'].sum() if not sub_df.empty else 0

		#Tính pallet block raw_mat và label
		block_rm_df = filtered_df[filtered_df['type1'] == 'raw_mat']
		block_lb_df = filtered_df[filtered_df['name_wh'] == 'lb']
		results['block_plrm'] = block_rm_df['pallet'].sum() if not block_rm_df.empty else 0
		results['block_pllb'] = block_lb_df['pallet'].sum() if not block_lb_df.empty else 0

		#Tính lại pallet block_rpm. Lấy block_rpm - block_lb
		results['block_plpm'] = results['block_plrpm'] - results['block_pllb'] - results['block_plrm']
		
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
		"""	Count Pallet theo Cat dwn, febz, hdl dựa vào cat_inv là FG và cột cat (masterdata)
			Không lấy pallet ở steam và lsl có name_wh lần lượt là rej, lsl
			Pallet FG_Other sẽ được tính trong VariableContainer. Lấy tổng FG trừ 3 cái còn lại
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
			key_result = f"fg_{cat}"
			results[key_result] = sub_df['pallet'].sum() if not sub_df.empty else 0

		return results
	
	def count_pallet_jit(self) -> Dict[str, float]:
		"""	Không lấy pallet ở steam và lsl có name_wh lần lượt là rej, lsl
			Lấy tổng pallet ở cột jit có nội dung là jit và cat_inv là rpm
		"""
		if "jit" not in self.df.columns:
			logger.warning(f"Cột 'jit' không tồn tại. Không thể tính pallet JIT.")
			return {}
		
		filtered_df = self.df[self.df['cat_inv'] == 'rpm'].copy()
		mask = pd.Series(True, filtered_df.index)
		mask = (filtered_df['name_wh'] != 'rej')&(filtered_df['name_wh'] != 'lsl')
		mask &= filtered_df['jit'] == 'jit'
		filtered_df = filtered_df[mask]

		results = {}

		pallet_jit = filtered_df['pallet'].sum() if not filtered_df.empty else 0

		results['pallet_jit'] = pallet_jit

		return results
	
	def count_pallet_rpm_with_type2(self) -> Dict[str, float]:
		"""	Không lấy pallet ở steam và lsl có name_wh lần lượt là rej, lsl
			Cout pallet theo cat_inv và type2 shipper, pouch, bottle.
			Muốn tính được other phải lấy tổng trừ đi 3 cái còn lại
		"""
		if "type2" not in self.df.columns:
			logger.warning(f"Cột 'type2' không tồn tại. Không thể tính pallet shipper, pouch, bottle.")
			return {}
		
		filtered_df = self.df[self.df['cat_inv'] == 'rpm'].copy()
		mask = pd.Series(True, filtered_df.index)
		mask &= (filtered_df['name_wh'] != 'rej')&(filtered_df['name_wh'] != 'lsl')
		mask &= filtered_df['type2'].isin(['shipper', 'pouch', 'bottle'])

		filtered_df = filtered_df[mask]

		results = {}

		for type2 in ['shipper', 'pouch', 'bottle']:
			sub_df = filtered_df[filtered_df['type2'] == type2]
			key_result = f"pm_{type2}"
			results[key_result] = sub_df['pallet'].sum() if not sub_df.empty else 0

		return results
	
	def count_pallet_rack_da(self) -> Dict[str, float]:
		"""	Cout pallet có cột type_loc là ob
		"""
		filtered_df = self.df[self.df['type_loc'] == 'ob'].copy()

		results = {}

		for type_rack in ['pf', 'hr']:
			df_type_rack = filtered_df[filtered_df['type_rack'] == type_rack]
			for cat_inv in ['fg', 'rpm', 'eo']:
				df_cat_inv = df_type_rack[df_type_rack['cat_inv'] == cat_inv]
				key_result = f"da_{type_rack}_{cat_inv}"
				results[key_result] = df_cat_inv['pallet'].sum() if not df_cat_inv.empty else 0

		return results
	
	def count_pallet_rack_ho(self) -> Dict[str, float]:
		"""	Cout pallet có cột type_loc là ho
		"""
		filtered_df = self.df[self.df['type_loc'] == 'ho'].copy()

		results = {}

		for type_rack in ['pf']:
			df_type_rack = filtered_df[filtered_df['type_rack'] == type_rack]
			for cat_inv in ['fg', 'rpm', 'eo']:
				df_cat_inv = df_type_rack[df_type_rack['cat_inv'] == cat_inv]
				key_result = f"ho_{type_rack}_{cat_inv}"
				results[key_result] = df_cat_inv['pallet'].sum() if not df_cat_inv.empty else 0

		return results
	
	def count_pallet_total_fg(self) -> Dict[str, float]:
		"""	Count tất cả pallet có cat_inv là FG.
			Tránh trường hợp count sót khi gcas chưa có trong masterdata
			Chỉ count những vị trí có trong 'wh1', 'wh2', 'wh3'
		"""

		filtered_df = self.df[self.df['cat_inv'] == 'fg'].copy()
		mask = pd.Series(True, filtered_df.index)
		mask &= filtered_df['name_wh'].isin(['wh1', 'wh2', 'wh3', ''])
		filtered_df = filtered_df[mask]

		results = {}

		key_result = f"pallet_totalfg"
		results[key_result] = filtered_df['pallet'].sum() if not filtered_df.empty else 0

		return results
	
	def count_pallet_total_pm(self) -> Dict[str, float]:
		"""	Tính tổng cột pallet có cat_inv là rpm.
			Không lấy pallet ở steam và lsl có name_wh lần lượt là rej, lsl, label.
			Sở dĩ không lọc trong wh1,2,3 vì có trường hợp pm sẽ đem vào lưu cooling3, cooling1 trong những ngày kho đầy
			Cột type1 khác raw_mat
		"""

		filtered_df = self.df[self.df['cat_inv'] == 'rpm'].copy()
		mask = pd.Series(True, filtered_df.index)
		mask &= filtered_df['type1'] != 'raw_mat'
		mask &= filtered_df['name_wh'].isin(['wh1', 'wh2', 'wh3', ''])
		filtered_df = filtered_df[mask]

		results = {}

		key_result = f"pallet_totalpm"
		results[key_result] = filtered_df['pallet'].sum() if not filtered_df.empty else 0

		return results
	
	def count_pallet_total_rm(self) -> Dict[str, float]:
		"""	Tính tổng cột pallet có cat_inv là rpm.
			Chỉ lấy trong wh1,2,3 và những dòng trống vì location chưa update trong masterlocation
			Sở dĩ không lấy như pm là loại những pallet ở steam, lsl, label vì hàng rm khi lưu vào các
			kho đặc biệt như cool1,2,3 or pf1,2,3,4,5 đã được count riêng rồi.
			Cột type1 bằng raw_mat
		"""

		filtered_df = self.df[self.df['cat_inv'] == 'rpm'].copy()
		mask = pd.Series(True, filtered_df.index)
		mask &= filtered_df['type1'] == 'raw_mat'
		mask &= filtered_df['name_wh'].isin(['wh1', 'wh2', 'wh3', ''])
		filtered_df = filtered_df[mask]

		results = {}

		key_result = f"pallet_totalrm"
		results[key_result] = filtered_df['pallet'].sum() if not filtered_df.empty else 0

		return results
	
	def count_pallet_eo(self) -> Dict[str, float]:
		"""Tính tổng cột pallet có cat_inv là EO
		"""
		filtered_df = self.df[self.df['cat_inv'] == 'eo'].copy()

		results = {}

		key_result = f"pallet_totaleo"
		results[key_result] = filtered_df['pallet'].sum() if not filtered_df.empty else 0

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

		#Count pallet JIT
		pallet_jit = self.count_pallet_jit()
		results.update(pallet_jit)

		# Count pallet type2 (shipper, pouch, bottle)
		pallet_type2 = self.count_pallet_rpm_with_type2()
		results.update(pallet_type2)

		#Count pallet rack DA
		pallet_rack_da = self.count_pallet_rack_da()
		results.update(pallet_rack_da)

		#Count pallet vị trí HO
		pallet_location_ho = self.count_pallet_rack_ho()
		results.update(pallet_location_ho)

		#Count pallet total FG
		pallet_total_fg = self.count_pallet_total_fg()
		results.update(pallet_total_fg)

		#Count pallet total pm
		pallet_total_pm = self.count_pallet_total_pm()
		results.update(pallet_total_pm)

		#Count pallet total rm
		pallet_total_rm = self.count_pallet_total_rm()
		results.update(pallet_total_rm)

		#Count pallet total eo
		pallet_total_eo = self.count_pallet_eo()
		results.update(pallet_total_eo)

		#Count location mixup
		location_mixup = self.count_location_mixup()
		results.update(location_mixup)

		# #Count pallet empty bin
		# pallet_empty = self.count_pallet_bin_empty()
		# # results.update(pallet_empty)

		#Count bin cần combine
		pallet_combinebin = self.count_bin_combine()
		results.update(pallet_combinebin)

		#Count bin empty
		pallet_emptybin = self.count_pallet_bin_empty()
		results.update(pallet_emptybin)

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
				fig = GaugeChart(pallet_type.title_chart, pallet_type.pallet, pallet_type.capa_chart).create_fig()
				dict_all_chart[name] = fig
			elif  pallet_type.type_chart == 2:
				fig = Metric(pallet_type.title_chart, pallet_type.pallet).create_metric_card()
				dict_all_chart[name] = fig
			elif  pallet_type.type_chart == 3:
				dict_all_chart[name] = pallet_type.cu_chart
		
		obj_all_chart = VariableChartContainer(dict_all_chart)
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