import logging
import keyword
import re
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

class VariableContainer:
	"""
	Một container sử dụng các key của dictionary làm tên thuộc tính
	để dễ dàng truy cập và thực hiện các phép tính.
	Muốn truy cập biến chi tiết (fg, rpm, eo): self.variables. Vì self.variables được init khi khởi tạo
	Khi tính toán xong phải delete atts self.variables
	Muốn truy cập biến đã tổng hợp khi đã loại bỏ (fg, rpm, eo): self
	"""
	def __init__(self, variables_dict: Dict[str, float]):
		"""
		Khởi tạo đối tượng từ một dictionary.

		Args:
			variables_dict (dict): Dictionary có key là tên biến (string)
								   và value là giá trị của biến (số).
		"""
		if not isinstance(variables_dict, dict):
			logger.error(f"Đầu vào phải là một dictionary.")
			raise

		self.variables_dict = variables_dict
		#Cover dict thành dataframe
		df = pd.DataFrame(list(variables_dict.items()), columns=['namewh_typerack_catinv', 'pallet_count'])
		#Adding thêm một cột mới chỉ có namewh và type_rack
		df['namewh_typerack'] = df['namewh_typerack_catinv'].apply(lambda x: x.split("_")[0] + "_" + x.split("_")[1])
		#Sắp xếp lại df cho dễ nhìn, khó tính lắm
		df = df[['namewh_typerack_catinv', 'namewh_typerack', 'pallet_count']]
		#Tính tổng cột pallet thêm namewh và type_rack
		df = df.groupby('namewh_typerack')['pallet_count'].sum().reset_index()
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
        - High Rack kho 2 cộng luôn tồn tầng A của rack DA
		- Pickface của rack kho 2 trừ đi pf_da và trừ luôn HO
        - Floor: lấy tồn pallet các vị trí in (nhập 2,3,4), pick (fill hàng), vị trí HO, các vị trí đường luồng wh2_
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
		wh2_floor = self.wh2_in + self.wh2_pick + self.wh2_ww + self.wh2_return + self.wh2_rework + self.ho_pf
		self.wh2_hr = self.wh2_hr + self.da_pf
		self.wh2_pf = self.wh2_pf - self.da_pf - self.ho_pf
		wh2_total = self.wh2_pf + self.wh2_hr + wh2_floor
		setattr(self, 'wh2_total', wh2_total)
		setattr(self, 'wh2_floor', wh2_floor)
		for name in ("wh2_in", "wh2_pick", "wh2_ww", "wh2_return", "wh2_rework", "da_pf", "da_hr", "ho_pf"):
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
	
	def _get_total_eo(self):
		"""Lấy tổng tồn eo - eo_steam - eo lưu cont
		"""
		
		eo_total = self.pallet_totaleo - self.variables_dict.get("rej_reject_eo", 0) - self.variables_dict.get("wh2_scanout_eo", 0)
		
		setattr(self, 'eo_total', eo_total)

		for name in ("pallet_totaleo",):
			self.delete_attribute(name)
	
	def _get_total_rm(self):
		"""	Pallet raw_mat chỉ lấy trong wh1, wh2, wh3 và những dòng nan sau khi đã filter cột type1=="raw_mat"
			total_rm = Lấy tổng pallet_rm
			Không cần trừ pallet rm ở steam vì có lọc vào đâu :))
			Trừ luôn pallet rpm trên scanout đem lên lưu cont
		"""
		rm_total = self.pallet_totalrm

		setattr(self, 'rm_total', rm_total)

		for name in ("pallet_totalrm",):
			self.delete_attribute(name)

	def _get_total_fg(self):
		"""Tổng pallet FG trong wh1, wh2, wh3 trừ đi vị trí scanout
		"""
		fg_total = self.pallet_totalfg - self.variables_dict.get("wh2_scanout_fg", 0)

		setattr(self, 'fg_total', fg_total)

		for name in ("pallet_totalfg",):
			self.delete_attribute(name)

	def _get_total_bdfg(self):
		"""Pallet FGBD fg_total trừ đi block_fg
		"""
		fgbd_total = self.fg_total - self.block_plfg

		setattr(self, 'fgbd_total', fgbd_total)

	def _get_total_pm(self):
		"""Tổng pallet PM trong wh1, wh2, wh3
		"""
		pm_total = self.pallet_totalpm - self.variables_dict.get("wh2_scanout_rpm", 0)

		setattr(self, 'pm_total', pm_total)

		for name in ("pallet_totalpm",):
			self.delete_attribute(name)

	def _get_total_bdpm(self):
		"""Pallet PMBD pm_total trừ đi block_pm
		"""
		pmbd_total = self.pm_total - self.block_plpm - self.block_plrm

		setattr(self, 'pmbd_total', pmbd_total)

	def _get_total_bdwh(self):
		"""Tổng của fg_total + pm_totam + rm_total
		"""
		wh_total = self.fg_total + self.pm_total + self.rm_total

		setattr(self, 'wh_total', wh_total)

	def _get_total_block(self):
		"""Gom lại pallet block còn 4 cái
			Total block, fg block, rpm block, label block
		"""
		block_fg = self.block_plfg
		block_rpm = self.block_plrm + self.block_plpm
		block_lb = self.block_pllb
		block_total = block_fg + block_rpm + block_lb

		setattr(self, "block_fg", block_fg)
		setattr(self, "block_rpm", block_rpm)
		setattr(self, "block_lb", block_lb)
		setattr(self, "block_total", block_total)

		for name in ("block_plfg", "block_plrm", "block_plpm", "block_pllb", "block_pleo", "block_plrpm"):
			self.delete_attribute(name)
	
	def _get_other_fg_with_cat(self):
		"""Lấy fg_total (chưa trừ scanout) trừ đi dwn, febz, hdl
		"""
		fg_other = self.pallet_totalfg - self.fg_dwn - self.fg_hdl - self.fg_febz

		setattr(self, "fg_other", fg_other)

	def _get_other_pm_with_type2(self):
		"""Lấy rpm_total chưa trừ cont trừ đi dwn, febz, hdl
		"""
		pm_other = self.pallet_totalpm - self.pm_bottle - self.pm_pouch - self.pm_shipper

		setattr(self, "pm_other", pm_other)
	
	def _get_pallet_steam(self):
		"""Chuyển attr rej_reject thành stream cho dễ nhớ
		"""
		pallet_steam = self.rej_reject

		setattr(self, "pallet_steam", pallet_steam)

		self.delete_attribute("rej_reject")
	
	def _get_pallet_scanout(self):
		"""Chuyển pallet wh2_scanout thành scanout cho dễ nhớ
		"""
		pallet_scanout = self.wh2_scanout

		setattr(self, "pallet_scanout", pallet_scanout)

		self.delete_attribute("wh2_scanout")
	
	def get_cu_for_chart(self):
		# name_wh_need_capa = ['wh1', 'wh2', 'wh3', 'cool', 'pf', 'lb', 'eo', 'wh']
		name_wh_need_capa = [key for key in CAPACITY_WAREHOUSE.keys()]
		capa_wh = {f"capa_{name}": CAPACITY_WAREHOUSE.get(name, 1).get('total',1) for name in name_wh_need_capa}
		cu_wh = {f"cu_{name}": f"{self.__dict__.get(f'{name}_total')/capa_wh.get(f'capa_{name}',1):.0%}" for name in name_wh_need_capa}
		for key, value in cu_wh.items():
			setattr(self, key, value)

	def get_comprehensive_data_chart(self):
		"""
		chart_type = 1 -> chart Gauge
		chart_type = 2 -> Metric
		Thứ tự gọi hàm ở dưới rất quan trọng. 
		_get_other_fg_with_cat() và _get_other_pm_with_type2() phải gọi trước
		_get_total_rm() và _get_total_fg() vì khi gọi 2 hàm này thì attr pallet_totalfg và pallet_totalpm
		sẽ bị delete khỏi hệ thống không còn attr để gọi tính toán cho 2 hàm trên.
		"""
		dict_data: Dict[str, Dict[float, int]] = {}
		self._set_total_floor_wh1()
		self._set_total_floor_wh2()
		self._set_total_floor_wh3()
		self._get_total_floor_cooling()
		self._get_total_floor_perfume()
		self._get_total_label()
		self._get_total_eo()
		self._get_other_fg_with_cat()
		self._get_other_pm_with_type2()
		self._get_total_rm()
		self._get_total_fg()
		self._get_total_bdfg()
		self._get_total_pm()
		self._get_total_bdpm()
		self._get_total_bdwh()
		self._get_total_block()
		self._get_pallet_steam()
		self._get_pallet_scanout()
		self.get_cu_for_chart()
		#Xóa thuộc tính "variables_dict" đã gán trên init để lấy số lượng pallet EO tính WH2
		self.delete_attribute('variables_dict')

		#Check tên biến và giá trị trả về của class
		# i=1
		# for  key, value in self.__dict__.items():
		# 	print(f"Key {i}: {key}  Value: {value}")
		# 	i += 1

		for key in self.__dict__:
			str_name = key.split("_")
			use_chart_gauge = (
				"wh1_floor", "wh1_pf", "wh1_hr", "wh1_total",
				"wh2_floor", "wh2_pf", "wh2_hr", "wh2_total",
				"wh3_floor", "wh3_pf", "wh3_hr", "wh3_total",
				"cool_total", "pf_total", "lb_total", "eo_total", "wh_total")
			#any([key.find("_total")!=-1, key.find("wh")!=-1])
			if key in use_chart_gauge:
				type_chart = 1
				if key in ("wh1_total", "wh2_total", "wh3_total", "cool_total", "pf_total", "wh_total", "lb_total", "eo_total"):
					name_wh = key.split("_")[0]
					title = name_wh.upper() + " CU: "
					dict_data[key] = DataChartType(
						pallet=getattr(self, key),
						type_chart=type_chart,
						title_chart=title,
						capa_chart=CAPACITY_WAREHOUSE.get(str_name[0], 1).get(str_name[1], 1)
						)
				else:
					dict_data[key] = DataChartType(
						pallet=getattr(self, key),
						type_chart=type_chart,
						capa_chart=CAPACITY_WAREHOUSE.get(str_name[0], 1).get(str_name[1], 1)
						)
					
			elif key.startswith("cu_"):
				type_chart = 3
				dict_data[key] = DataChartType(type_chart=type_chart, cu_chart=self.__dict__.get(key, 0))
			else:
				type_chart = 2
				name_wh_detail = str_name[0]
				name_wh = re.match(r'\D+', str_name[0]).group()
				title = f"{TITLE_METRIC_CHART.get(key, None)}"
				if name_wh in ['cool', 'pf']:
					if str_name[1] == 'floor':
						capa_wh = CAPACITY_WAREHOUSE.get(name_wh, None).get(key, None)
						title = f"{TITLE_METRIC_CHART.get(key, None)} {capa_wh}"
					else:
						capa_wh = CAPACITY_WAREHOUSE.get(name_wh, None).get(name_wh_detail, None)
						title = f"{TITLE_METRIC_CHART.get(name_wh_detail, None)} {capa_wh}"

				dict_data[key] = DataChartType(
					pallet=getattr(self, key),
					type_chart=type_chart,
					title_chart=title
					)

		return dict_data
	
	def delete_attribute(self, attribute_name):
		if hasattr(self, attribute_name): # Kiểm tra xem thuộc tính có tồn tại không
			value = getattr(self, attribute_name)
			delattr(self, attribute_name) # Cách an toàn hơn để xóa thuộc tính
			# Hoặc: del self.__dict__[attribute_name] # Cách trực tiếp hơn nếu bạn chắc chắn
			# logger.info(f"Đã xóa thuộc tính '{attribute_name}' với giá trị {value} trong class 'VariableContainer'.")
		else:
			logger.error(f"Thuộc tính '{attribute_name}' không tồn tại.")
			

@dataclass
class DataChartType:
	"""Nhận vào value, type chart
		Trả về dict của 2 biến trên.
	"""
	type_chart: int
	pallet: Optional[float] = None
	capa_chart: Optional[int] = None
	title_chart: Optional[str] = None
	cu_chart: Optional[Any] = None

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
		'total': 376,
		'cool1': 96,
		'cool2': 178,
		'cool3': 126,
		'cool_floor': 20 #'cool_floor
	},
	'pf': {
		'total': 364,
		'pf1': 32,
		'pf2': 42,
		'pf3': 36,
		'pf4': 66,
		'pf5': 188,
		'pf_floor': 37
	},
	'lb': {
		'total': 1156
	},
	'eo': {
		'total': 546
	},
	'wh': {
		'total': 8776
	}
}

TITLE_METRIC_CHART = {
	'cool1': 'C1 - ',
	'cool2': 'C2 - ',
	'cool3': 'C3 - ',
	'cool_floor': 'Floor - ',
	'pf1': 'PF1 - ',
	'pf2': 'PF2 - ',
	'pf3': 'PF3 - ',
	'pf4': 'PF4 - ',
	'pf5': 'PF5 - ',
	'pf_floor': 'Floor - ',
	'fg_dwn': 'FG DWN',
	'fg_febz': 'FG FEBZ',
	'fg_hdl': 'FG HDL',
	'fg_other': 'FG OTHER',
	'lsl_in': 'PL EOL',
	'lsl_lrt': 'LRT',
	'lsl_lslpm': 'LSL PM',
	'lsl_lslrm': 'LSL RM',
	'pallet_fgdm': 'FGDM',
	'pallet_fgls': 'FGLS',
	'pallet_lost': 'LOST',
	'pallet_matdm': 'MATDM',
	'pallet_jit': 'JIT',
	'pm_bottle': 'BOTTLE',
	'pm_pouch': 'POUCH',
	'pm_shipper': 'SHIPPER',
	'pm_other': 'OTHER',
	'pallet_scanout': 'CONT**',
	'pallet_steam': 'STEAM 1,2',
	'block_fg': 'FG',
	'block_rpm': 'RPM',
	'block_lb': 'LABEL',
	'block_total': 'BLOCK 200',
	'fg_total': 'TOTAL FG',
	'pm_total': 'TOTAL PM',
	'rm_total': 'NORM. RM',
	'fgbd_total': 'FG BD 2500',
	'pmbd_total': 'PM PLT 4500',
	'pallet_mixup': 'MIXUP',
	'pallet_combinebin': 'COMBINE',
	'pallet_emptybin': 'EMPTY BIN'
}