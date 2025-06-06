import logging
import keyword
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class VariableContainer:
	"""
	Một container sử dụng các key của dictionary làm tên thuộc tính
	để dễ dàng truy cập và thực hiện các phép tính.
	"""
	def __init__(self, variables_dict: Dict[str, float]):
		"""
		Khởi tạo đối tượng từ một dictionary.

		Args:
			variables_dict (dict): Dictionary có key là tên biến (string)
								   và value là giá trị của biến (số).
		"""
		self.variables_dict = variables_dict
		#Cover dict thành dataframe
		df = pd.DataFrame(list(variables_dict.items()), columns=['namewh_typerack_catinv', 'pallet_count'])
		#Adding thêm một cột mới chỉ có namewh và type_rack
		df['namewh_typerack'] = df['namewh_typerack_catinv'].apply(lambda x: x.split("_")[0] + "_" + x.split("_")[1])
		#Sắp xếp lại df cho dễ nhìn, khó tính lắm
		df = df[['namewh_typerack_catinv', 'namewh_typerack', 'pallet_count']]
		#Tính tổng cột pallet thêm namewh và type_rack
		df = df.groupby('namewh_typerack')['pallet_count'].sum().reset_index()
		print(df)
		#Chuyển ngược dataframe lại thành dict
		dict_namewh_typerack = df.set_index('namewh_typerack')['pallet_count'].to_dict()
		#Set đối tượng cho từng items của dict. Key làm tên biến, value làm value của biến

		if not isinstance(dict_namewh_typerack, dict):
			logger.error(f"Đầu vào phải là một dictionary.")
			raise
		for key, value in dict_namewh_typerack.items():
			# Kiểm tra xem key có phải là tên thuộc tính (biến) hợp lệ trong Python không
			# isidentifier() kiểm tra cú pháp tên biến
			# keyword.iskeyword() kiểm tra xem tên có phải là từ khóa reserved không
			if isinstance(key, str) and key.isidentifier() and not keyword.iskeyword(key):
				setattr(self, key, value)
				# logger.info(f"Đã gán: self.{key} = {value}") # Có thể bỏ comment để debug
			else:
				logger.warning(f"Cảnh báo: Key '{key}' không phải là tên biến hợp lệ. Bỏ qua.")

		# self._set_total_floor_wh1()
		# self._set_total_floor_wh2()
		# self._set_total_floor_wh3()
		# self._get_total_floor_cooling()
		# self._get_total_floor_perfume()
		# self.get_sumary()

	def _set_total_floor_wh1(self):
		"""Tính total pallet cho wh1, tính pallet_floor
			Xóa wh1_in, wh1_ww sau khi tính pallet_floor
		"""
		wh1_floor = self.wh1_in + self.wh1_ww
		total_wh1 = wh1_floor + self.wh1_pf + self.wh1_hr
		setattr(self, 'wh1_total', total_wh1)
		setattr(self, 'wh1_floor', wh1_floor)
		self.delete_attribute("wh1_in")
		self.delete_attribute("wh1_ww")
		

	def _set_total_floor_wh2(self):
		"""
		Kho 2 có những vị trí đặc biệt và cách tính toán khác với wh1, wh3
        Điểm chung tính total pallet hightrack, level A và Floor
        Điểm riêng:
        - High Rack kho 2 cộng luôn tồn tầng A, hight rack của rack DA, trừ số pallet các vị trí HO
        - Floor: lấy tồn pallet các vị trí in (nhập 2,3,4), pick (fill hàng), các vị trí đường luồng wh2_
        các vị trí STJP, FGDM, FGLS
        Lưu ý: khi tính tồn kho hr, pf của wh2 đã có tồn kho của rack DA rồi. Nên chỉ cần lấy tồn pf_da trừ khỏi pf_wh2
        và cộng ngược lại hr_wh để đảm bảo tồn rack DA được cộng hết cho hr_wh2
		=====================================
        Tính riêng tồn kho của rack DA và bin HO.
        Tồn rack DA sẽ được cộng vào tầng cao của WH2
        Tồn HO sẽ được cộng vào Floor của WH2
    
        typerack_da = ('hr', 'pf')
        typeloc_da = ('ob',)
        typerack_ho = ('pf',)
        typeloc_ho = ('ho',)
		"""
		wh2_floor = self.wh2_in + self.wh2_pick + self.wh2_ww + self.wh2_return + self.wh2_rework
		wh2_total = self.wh2_pf + self.wh2_hr + wh2_floor
		setattr(self, 'wh2_total', wh2_total)
		setattr(self, 'wh2_floor', wh2_floor)
		for name in ("wh2_in", "wh2_pick", "wh2_ww", "wh2_return"):
			self.delete_attribute(name)
	
	def _set_total_floor_wh3(self):
		"""
        WH3 floor có cộng thêm hàng EO ở dưới sàn
        Trên rack chưa cộng EO vào
        Nhưng không cộng tồn EO dưới sàn vào tổng tồn WH3
		"""
		wh3_floor = self.wh3_in + self.wh3_ww
		wh3_pf = self.wh3_pf - self.variables_dict.get("wh3_pf_eo", 0)
		wh3_hr = self.wh3_hr - self.variables_dict.get("wh3_hr_eo", 0)
		wh3_total = wh3_hr + wh3_pf + wh3_floor - (
			self.variables_dict.get("wh3_in_eo", 0) +
			self.variables_dict.get("wh3_ww_eo", 0)
		)

		setattr(self, 'wh3_total', wh3_total)
		setattr(self, 'wh3_floor', wh3_floor)
		setattr(self, 'wh3_pf', wh3_pf)
		setattr(self, 'wh3_hr', wh3_hr)

		for name in ("wh3_in", "wh3_ww"):
			self.delete_attribute(name)
	
	def _get_total_floor_cooling(self):
		"""Cộng floor cl1,2,3 lại làm một
		Tính tổng 3 kho cooling
		"""
		cool_floor = self.cool1_ww + self.cool2_ww + self.cool3_ww
		cool_total = self.cool1_mk + self.cool2_mk + self.cool3_mk + cool_floor

		setattr(self, 'cool_floor', cool_floor)
		setattr(self, 'cool_total', cool_total)

		for name in ("cool1_ww", "cool2_ww", "cool3_ww"):
			self.delete_attribute(name)

	def _get_total_floor_perfume(self):
		"""Cộng floor pf1,2,3,4,5 lại làm một
		Tính tổng 5 kho perfume
		"""
		pf_floor = self.pf1_ww + self.pf2_ww + self.pf3_ww + self.pf4_ww + self.pf5_ww
		pf_total = self.pf1_mk + self.pf2_mk + self.pf3_mk + self.pf4_mk + self.pf5_mk + pf_floor

		setattr(self, 'pf_floor', pf_floor)
		setattr(self, 'pf_total', pf_total)

		for name in ("pf1_ww", "pf2_ww", "pf3_ww", "pf4_ww", "pf5_ww"):
			self.delete_attribute(name)

	def _get_total_label(self):
		lb_total = self.lb_ww + self.lb_pf + self.lb_hr

		setattr(self, 'lb_total', lb_total)

		for name in ("lb_ww", "lb_pf", "lb_hr"):
			self.delete_attribute(name)



	def get_comprehensive_data_chart(self):
		"""
		chart_type = 1 -> chart Gauge
		chart_type = 2 -> Metric
		"""
		dict_data: Dict[str, Dict[float, int]] = {}
		self._set_total_floor_wh1()
		self._set_total_floor_wh2()
		self._set_total_floor_wh3()
		self._get_total_floor_cooling()
		self._get_total_floor_perfume()
		self._get_total_label()

		#Xóa thuộc tính "variables_dict" đã gán trên init để lấy số lượng pallet EO tính WH2
		self.delete_attribute('variables_dict')
		for k in self.__dict__:
			str_name = k.split("_")
			use_chart_gauge = (
				"wh1_floor", "wh1_pf", "wh1_hr", "wh1_total",
				"wh2_floor", "wh2_pf", "wh2_hr", "wh2_total",
				"wh3_floor", "wh3_pf", "wh3_hr", "wh3_total",
				"cool_total", "pf_total")
			#any([k.find("_total")!=-1, k.find("wh")!=-1])
			if k in use_chart_gauge:
				type_chart = 1
				dict_data[k] = DataChartType(
					pallet=getattr(self, k),
					type_chart=type_chart,
					capa_chart=CAPACITY_WAREHOUSE.get(str_name[0], 1).get(str_name[1], 1))
			else:
				type_chart = 2
				dict_data[k] = DataChartType(pallet=getattr(self, k), type_chart=type_chart)
		return dict_data
	
	def delete_attribute(self, attribute_name):
		if hasattr(self, attribute_name): # Kiểm tra xem thuộc tính có tồn tại không
			value = getattr(self, attribute_name)
			delattr(self, attribute_name) # Cách an toàn hơn để xóa thuộc tính
			# Hoặc: del self.__dict__[attribute_name] # Cách trực tiếp hơn nếu bạn chắc chắn
			logger.info(f"Đã xóa thuộc tính '{attribute_name}' với giá trị {value} trong class 'VariableContainer'.")
		else:
			logger.error(f"Thuộc tính '{attribute_name}' không tồn tại.")
			

@dataclass
class DataChartType:
	"""Nhận vào value, type chart
		Trả về dict của 2 biến trên.
	"""
	pallet: float
	type_chart: int
	capa_chart: Optional[int] = None
	title_chart: Optional[str] = None

	def to_dict(self):
		return {
			"pallet": self.pallet,
			'type_chart': self.type_chart,
			'capa_chart': self.capa_chart,
			'title_chart': self.title_chart
		}

CAPACITY_WAREHOUSE = {
	'wh1': {
		'total': 1215,
		'hr': 966,
		'pf': 207,
		'floor': 42
	},
	'wh2': {
		'total': 5082,
		'hr': 4068,
		'pf': 758,
		'floor': 256
	},
	'wh3': {
		'total': 2479,
		'hr': 2114,
		'pf': 343,
		'floor': 22
	},
	'cool': {
		'total': 376
	},
	'pf': {
		'total': 364
	},
	'lb': {
		'total': 1156
	},
	'eo_cons': {
		'total': 546
	},
	'wh': {
		'total': 8776
	}
}