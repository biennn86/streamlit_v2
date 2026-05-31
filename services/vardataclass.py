from dataclasses import dataclass, field, fields
from services.chart_services import GaugeChart, Metric
from typing import List, Tuple, Dict, Any, Optional

@dataclass
class VarWarehoueTypeFormDict:
	#WH1
	wh1_ww_rpm: int
	wh1_ww_fg: int
	wh1_ww_eo: int
	wh1_pf_rpm: int
	wh1_pf_fg: int
	wh1_pf_eo: int
	wh1_in_rpm: int
	wh1_in_fg: int
	wh1_in_eo: int
	wh1_hr_rpm: int
	wh1_hr_fg: int
	wh1_hr_eo: int
	#WH2
	wh2_hr_eo: int
	wh2_hr_fg: int
	wh2_hr_rpm: int
	wh2_in_eo: int
	wh2_in_fg: int
	wh2_in_rpm: int
	wh2_ww_eo: int
	wh2_ww_fg: int
	wh2_ww_rpm: int
	wh2_pf_eo: int
	wh2_pf_fg: int
	wh2_pf_rpm: int
	wh2_pick_eo: int
	wh2_pick_fg: int
	wh2_pick_rpm: int
	wh2_return_eo: int
	wh2_return_fg: int
	wh2_return_rpm: int
	wh2_rework_eo: int
	wh2_rework_fg: int
	wh2_rework_rpm: int
	wh2_scanout_eo: int
	wh2_scanout_fg: int
	wh2_scanout_rpm: int
	#WH3
	wh3_ww_rpm: int
	wh3_ww_fg: int
	wh3_ww_eo: int
	wh3_pf_rpm: int
	wh3_pf_fg: int
	wh3_pf_eo: int
	wh3_in_rpm: int
	wh3_in_fg: int
	wh3_in_eo: int
	wh3_hr_rpm: int
	wh3_hr_fg: int
	wh3_hr_eo: int
	#REJECT
	rej_reject_rpm: int
	rej_reject_fg: int
	rej_reject_eo: int
	#Cooling 1
	cool1_mk_eo: int
	cool1_mk_fg: int
	cool1_mk_rpm: int
	cool1_ww_eo: int
	cool1_ww_fg: int
	cool1_ww_rpm: int
	#Cooling 2
	cool2_mk_eo: int
	cool2_mk_fg: int
	cool2_mk_rpm: int
	cool2_ww_eo: int
	cool2_ww_fg: int
	cool2_ww_rpm: int
	#Cooling 3
	cool3_mk_eo: int
	cool3_mk_fg: int
	cool3_mk_rpm: int
	cool3_ww_eo: int
	cool3_ww_fg: int
	cool3_ww_rpm: int
	#Perfume 1
	pf1_mk_eo: int
	pf1_mk_fg: int
	pf1_mk_rpm: int
	pf1_ww_eo: int
	pf1_ww_fg: int
	pf1_ww_rpm: int
	#Perfume 2
	pf2_mk_eo: int
	pf2_mk_fg: int
	pf2_mk_rpm: int
	pf2_ww_eo: int
	pf2_ww_fg: int
	pf2_ww_rpm: int
	#Perfume 3
	pf3_mk_eo: int
	pf3_mk_fg: int
	pf3_mk_rpm: int
	pf3_ww_eo: int
	pf3_ww_fg: int
	pf3_ww_rpm: int
	#Perfume 4
	pf4_mk_eo: int
	pf4_mk_fg: int
	pf4_mk_rpm: int
	pf4_ww_eo: int
	pf4_ww_fg: int
	pf4_ww_rpm: int
	#Perfume 5
	pf5_mk_eo: int
	pf5_mk_fg: int
	pf5_mk_rpm: int
	pf5_ww_eo: int
	pf5_ww_fg: int
	pf5_ww_rpm: int
	#LSL raw_mat
	lsl_lslrm_rpm: int
	lsl_lslrm_fg: int
	lsl_lslrm_eo: int
	#LSL pack_mat
	lsl_lslpm_rpm: int
	lsl_lslpm_fg: int
	lsl_lslpm_eo: int
	#LRT
	lsl_lrt_rpm: int
	lsl_lrt_fg: int
	lsl_lrt_eo: int
	#EOL
	lsl_in_rpm: int
	lsl_in_fg: int
	lsl_in_eo: int
	#Label
	lb_ww_rpm: int
	lb_ww_fg: int
	lb_ww_eo: int
	lb_pf_rpm: int
	lb_pf_fg: int
	lb_pf_eo: int
	lb_hr_rpm: int
	lb_hr_fg: int
	lb_hr_eo: int
	#Block
	block_plfg: int
	block_pleo: int
	block_plrpm: int
	block_plrm: int
	block_pllb: int
	block_plpm: int
	#FGLS, FGDM, MATDM, LOST
	pallet_fgls: int
	pallet_fgdm: int
	pallet_matdm: int
	pallet_lost: int
	#DWN, FEBZ, HDL
	fg_dwn: int
	fg_febz: int
	fg_hdl: int
	#Shipper, pouch, bottle, jit
	pallet_jit: int
	pm_shipper: int
	pm_pouch: int
	pm_bottle: int
	#Rack DA
	da_pf_fg: int
	da_pf_rpm: int
	da_pf_eo: int
	da_hr_fg: int
	da_hr_rpm: int
	da_hr_eo: int
	#Location HO
	ho_pf_fg: int
	ho_pf_rpm: int
	ho_pf_eo: int
	#Total FG, PM, RM, EO
	pallet_totalfg: int
	pallet_totalpm: int
	pallet_totalrm: int
	pallet_totaleo: int
	#Mixup, combine bin, empty bin
	pallet_mixup: int
	pallet_combinebin: int
	pallet_emptybin: int

@dataclass
class VarContainerDrivative(VarWarehoueTypeFormDict):
	#WH1
	wh1_floor: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh1_pf: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh1_hr: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh1_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#WH2
	wh2_floor: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh2_pf: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh2_hr: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh2_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#WH3
	wh3_floor: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh3_pf: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh3_hr: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': None, 'chart_height': None})
	wh3_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#COOLING
	cool_floor: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	cool1: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	cool2: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	cool3: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	cool_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#PERFUME
	pf_floor: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf1: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf2: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf3: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf4: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf5: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	pf_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#TOTAL RAWMAT
	total_rm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#TOAL PACKMAT
	total_pm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_bdpm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#TOTAL FG
	total_fg: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_bdfg: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#TOTAL WAREHOUSE
	wh_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': True})
	#TOTAL LABEL
	label_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#EO TOTAL
	eo_total: int = field(init=False, metadata={'chart_type': 'gauge', 'chart_title': True, 'chart_height': None})
	#OTHER PACKMAT
	total_shipper: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_bottle: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_pouch: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_jit: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_pm_other: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#OTHER FG
	total_dwn: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_febz: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_hdl: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_fg_other: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#PALLET BLOCK
	total_block: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_block_fg: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_block_rpm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_block_lb: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	#OTHER
	total_cont: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_fgls: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_fgdm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_matdm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_lost: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_eol: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_lsl_pm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_lsl_rm: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_lrt: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})

	total_emptybin: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_combinebin: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})
	total_mixup: int = field(init=False, metadata={'chart_type': 'metric', 'chart_title': True, 'chart_height': None})

	def __post_init__(self):
		self.pallet_wh1()
		self.pallet_wh2()
		self.pallet_wh3()
		self.pallet_cool()
		self.pallet_pf()
		self.pallet_rawmat()
		self.pallet_packmat()
		self.pallet_bd_packmat()
		self.pallet_fg()
		self.pallet_bd_fg()
		self.pallet_total_bdwh()
		self.pallet_label()
		self.pallet_eo()
		self.pallet_shipper()
		self.pallet_bottle()
		self.pallet_pouch()
		self.pallet_pm_jit()
		self.pallet_pm_other()
		self.pallet_dwn()
		self.pallet_febz()
		self.pallet_hdl()
		self.pallet_fg_other()
		self.pallet_block_fg()
		self.pallet_block_rpm()
		self.pallet_block_lb()
		self.pallet_total_block()
		self.pallet_scanout()
		self.pallet_fgls_count()
		self.pallet_fgdm_count()
		self.pallet_matdm_count()
		self.pallet_lost_count()
		self.pallet_eol()
		self.palllet_lsl_pm()
		self.pallet_lsl_rm()
		self.pallet_lrt()
		self.pallet_emptybin_count()
		self.pallet_combinebin_count()
		self.pallet_mixup_count()

	def pallet_wh1(self):
		self.wh1_floor = self.wh1_in_fg + self.wh1_in_rpm + self.wh1_in_eo + self.wh1_ww_fg + self.wh1_ww_rpm + self.wh1_ww_eo
		self.wh1_pf = self.wh1_pf_fg + self.wh1_pf_rpm + self.wh1_pf_eo
		self.wh1_hr = self.wh1_hr_fg + self.wh1_hr_rpm + self.wh1_hr_eo
		self.wh1_total = self.wh1_floor + self.wh1_pf + self.wh1_hr

	def pallet_wh2(self):
		"""
		Kho 2 có những vị trí đặc biệt và cách tính toán khác với wh1, wh3
        Điểm chung tính total pallet hightrack, level A và Floor
        Điểm riêng:
        - High Rack kho 2 cộng luôn tồn tầng A của rack DA (nói chung lấy cả rack DA)
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
		self.wh2_floor = self.wh2_in_fg + self.wh2_in_rpm + self.wh2_in_eo +\
			  self.wh2_ww_rpm + self.wh2_ww_fg + self.wh2_ww_eo +\
			  self.wh2_pick_fg + self.wh2_pick_rpm + self.wh2_pick_eo +\
			  self.wh2_return_fg + self.wh2_return_rpm + self.wh2_return_eo +\
			  self.wh2_rework_fg + self.wh2_rework_rpm + self.wh2_rework_eo +\
			  self.ho_pf_fg + self.ho_pf_rpm + self.ho_pf_eo
		self.wh2_pf = (self.wh2_pf_fg + self.wh2_pf_rpm + self.wh2_pf_eo) - (self.da_pf_fg + self.da_pf_rpm + self.da_pf_eo) - (self.ho_pf_fg + self.ho_pf_rpm + self.ho_pf_eo)
		self.wh2_hr = (self.wh2_hr_fg + self.wh2_hr_rpm + self.wh2_hr_eo) + (self.da_pf_fg + self.da_pf_rpm + self.da_pf_eo)
		self.wh2_total = self.wh2_floor + self.wh2_pf + self.wh2_hr
	
	def pallet_wh3(self):
		"""
		WH3 floor có cộng thêm hàng EO ở dưới sàn
		Trên rack chưa cộng EO vào
		Nhưng không cộng tồn EO dưới sàn vào tổng tồn WH3
		"""
		self.wh3_floor = self.wh3_in_fg + self.wh3_in_rpm + self.wh3_in_eo +\
			self.wh3_ww_fg + self.wh3_ww_rpm + self.wh3_ww_eo
		self.wh3_pf = self.wh3_pf_rpm + self.wh3_pf_fg
		self.wh3_hr = self.wh3_hr_fg + self.wh3_hr_rpm
		self.wh3_total = (self.wh3_floor + self.wh3_pf + self.wh3_hr) - (self.wh3_in_eo + self.wh3_ww_eo)
	
	def pallet_cool(self):
		self.cool_floor = self.cool1_ww_fg + self.cool1_ww_rpm + self.cool1_ww_eo +\
			self.cool2_ww_fg + self.cool2_ww_rpm + self.cool2_ww_eo +\
			self.cool3_ww_fg + self.cool3_ww_rpm + self.cool3_ww_eo
		self.cool1 = self.cool1_mk_fg + self.cool1_mk_rpm + self.cool1_mk_eo
		self.cool2 = self.cool2_mk_fg + self.cool2_mk_rpm + self.cool2_mk_eo
		self.cool3 = self.cool3_mk_fg + self.cool3_mk_rpm + self.cool3_mk_eo
		self.cool_total = self.cool_floor + self.cool1 + self.cool2 + self.cool3
	
	def pallet_pf(self):
		self.pf_floor = self.pf1_ww_fg + self.pf1_ww_rpm + self.pf1_ww_eo +\
			self.pf2_ww_fg + self.pf2_ww_rpm + self.pf2_ww_eo +\
			self.pf3_ww_fg + self.pf3_ww_rpm + self.pf3_ww_eo +\
			self.pf4_ww_fg + self.pf4_ww_rpm + self.pf4_ww_eo +\
			self.pf5_ww_fg + self.pf5_ww_rpm + self.pf5_ww_eo
		self.pf1 = self.pf1_mk_fg + self.pf1_mk_rpm + self.pf1_mk_eo
		self.pf2 = self.pf2_mk_fg + self.pf2_mk_rpm + self.pf2_mk_eo
		self.pf3 = self.pf3_mk_fg + self.pf3_mk_rpm + self.pf3_mk_eo
		self.pf4 = self.pf4_mk_fg + self.pf4_mk_rpm + self.pf4_mk_eo
		self.pf5 = self.pf5_mk_fg + self.pf5_mk_rpm + self.pf5_mk_eo
		self.pf_total = self.pf1 + self.pf2 + self.pf3 + self.pf4 + self.pf5 + self.pf_floor
	
	def pallet_rawmat(self):
		"""	Pallet raw_mat chỉ lấy trong wh1, wh2, wh3 và những dòng nan sau khi đã filter cột type1=="raw_mat"
			total_rm = Lấy tổng pallet_rm
			Không cần trừ pallet rm ở steam vì có lọc vào đâu :))
			Trừ luôn pallet rpm trên scanout đem lên lưu cont
		"""
		self.total_rm = self.pallet_totalrm

	def pallet_packmat(self):
		"""Tổng pallet PM trong wh1, wh2, wh3
		"""
		self.total_pm = self.pallet_totalpm - self.wh2_scanout_rpm

	def pallet_bd_packmat(self):
		"""Pallet PMBD pm_total trừ đi block_pm
		"""
		self.total_bdpm = self.pallet_totalpm - self.wh2_scanout_rpm - self.block_plpm
	
	def pallet_fg(self):
		"""Tổng pallet FG trong wh1, wh2, wh3 trừ đi vị trí scanout
		"""
		self.total_fg = self.pallet_totalfg - self.wh2_scanout_fg
	
	def pallet_bd_fg(self):
		"""Pallet FGBD fg_total trừ đi block_fg
		"""
		self.total_bdfg = self.pallet_totalfg - self.wh2_scanout_fg - self.block_plfg

	def pallet_total_bdwh(self):
		"""Tổng của fg_total + pm_totam + rm_total
		"""
		self.wh_total = self.total_fg + self.total_pm + self.total_rm
	
	def pallet_label(self):
		self.label_total = self.lb_ww_rpm + self.lb_ww_fg + self.lb_ww_eo +\
			self.lb_pf_rpm + self.lb_pf_fg + self.lb_pf_eo +\
			self.lb_hr_rpm + self.lb_hr_fg + self.lb_hr_eo
	
	def pallet_eo(self):
		self.eo_total = self.pallet_totaleo
	
	def pallet_shipper(self):
		self.total_shipper = self.pm_shipper
	
	def pallet_bottle(self):
		self.total_bottle = self.pm_bottle

	def pallet_pouch(self):
		self.total_pouch = self.pm_pouch

	def pallet_pm_jit(self):
		self.total_jit = self.pallet_jit

	def pallet_pm_other(self):
		self.total_pm_other = self.pallet_totalpm - self.pm_shipper - self.pm_bottle - self.pm_pouch
	
	def pallet_dwn(self):
		self.total_dwn = self.fg_dwn
	
	def pallet_febz(self):
		self.total_febz = self.fg_febz

	def pallet_hdl(self):
		self.total_hdl = self.fg_hdl

	def pallet_fg_other(self):
		self.total_fg_other = self.pallet_totalfg - self.fg_dwn - self.fg_febz - self.fg_hdl
	
	def pallet_block_fg(self):
		self.total_block_fg = self.block_plfg
	
	def pallet_block_rpm(self):
		self.total_block_rpm = self.block_plpm + self.block_plrm

	def pallet_block_lb(self):
		self.total_block_lb = self.block_pllb
	
	def pallet_total_block(self):
		self.total_block = self.block_plfg + self.block_plpm + self.block_plrm + self.block_pllb
	
	def pallet_scanout(self):
		self.total_cont = self.wh2_scanout_fg + self.wh2_scanout_rpm + self.wh2_scanout_eo
	
	def pallet_fgls_count(self):
		self.total_fgls = self.pallet_fgls

	def pallet_fgdm_count(self):
		self.total_fgdm = self.pallet_fgdm
	
	def pallet_matdm_count(self):
		self.total_matdm = self.pallet_matdm

	def pallet_lost_count(self):
		self.total_lost = self.pallet_lost

	def pallet_eol(self):
		self.total_eol = self.lsl_in_rpm + self.lsl_in_fg + self.lsl_in_eo

	def palllet_lsl_pm(self):
		self.total_lsl_pm = self.lsl_lslpm_rpm + self.lsl_lslpm_fg + self.lsl_lslpm_eo
	
	def pallet_lsl_rm(self):
		self.total_lsl_rm = self.lsl_lslrm_rpm + self.lsl_lslrm_fg + self.lsl_lslrm_eo

	def pallet_lrt(self):
		self.total_lrt = self.lsl_lrt_rpm + self.lsl_lrt_fg + self.lsl_lrt_eo
	
	def pallet_emptybin_count(self):
		self.total_emptybin = self.pallet_emptybin

	def pallet_combinebin_count(self):
		self.total_combinebin = self.pallet_combinebin

	def pallet_mixup_count(self):
		self.total_mixup = self.pallet_mixup
	
@dataclass
class GaugeConfig:
	value: int
	capacity: int
	name: str
	title: str = None
	height: int = None

@dataclass
class MetricConfig:
	value: int
	name: str
	title: str = None

@dataclass
class DictChartTypeHint:
	wh1_floor: Any
	wh1_pf: Any
	wh1_hr: Any
	wh1_total: Any
	wh2_floor: Any
	wh2_pf: Any
	wh2_hr: Any
	wh2_total: Any
	wh3_floor: Any
	wh3_pf: Any
	wh3_hr: Any
	wh3_total: Any
	cool_total: Any
	pf_total: Any
	wh_total: Any
	label_total: Any
	eo_total: Any
	cool_floor: Any
	cool1: Any
	cool2: Any
	cool3: Any
	pf_floor: Any
	pf1: Any
	pf2: Any
	pf3: Any
	pf4: Any
	pf5: Any
	total_rm: Any
	total_pm: Any
	total_bdpm: Any
	total_fg: Any
	total_bdfg: Any
	total_shipper: Any
	total_bottle: Any
	total_pouch: Any
	total_jit: Any
	total_pm_other: Any
	total_dwn: Any
	total_febz: Any
	total_hdl: Any
	total_fg_other: Any
	total_block: Any
	total_block_fg: Any
	total_block_rpm: Any
	total_block_lb: Any
	total_cont: Any
	total_fgls: Any
	total_fgdm: Any
	total_matdm: Any
	total_lost: Any
	total_eol: Any
	total_lsl_pm: Any
	total_lsl_rm: Any
	total_lrt: Any
	total_emptybin: Any
	total_combinebin: Any
	total_mixup: Any

class ChartConfig:
	CAPACITY_WAREHOUSE = {
	'wh1': {'total': 1215, 'hr': 966, 'pf': 207, 'floor': 42},
	'wh2': {'total': 5178, 'hr': 4164, 'pf': 854, 'floor': 256},
	'wh3': {'total': 2479, 'hr': 2114, 'pf': 343, 'floor': 22},
	'cool': {'total': 306, 'cool1': 94, 'cool2': 176, 'cool3': 106, 'cool_floor': 30}, #'cool_floor
	'pf': {'total': 364, 'pf1': 32, 'pf2': 42, 'pf3': 36, 'pf4': 66, 'pf5': 188, 'pf_floor': 37},
	'label': {'total': 1156},
	'eo': {'total': 546},
	'wh': {'total': 8872}
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
	'total_dwn': 'FG DWN',
	'total_febz': 'FG FEBZ',
	'total_hdl': 'FG HDL',
	'total_fg_other': 'FG OTHER',
	'total_eol': 'PL EOL',
	'total_lrt': 'LRT',
	'total_lsl_pm': 'LSL PM',
	'total_lsl_rm': 'LSL RM',
	'total_fgdm': 'FGDM',
	'total_fgls': 'FGLS',
	'total_lost': 'LOST',
	'total_matdm': 'MATDM',
	'total_jit': 'JIT',
	'total_bottle': 'BOTTLE',
	'total_pouch': 'POUCH',
	'total_shipper': 'SHIPPER',
	'total_pm_other': 'OTHER',
	'total_cont': 'CONT**',
	'pallet_steam': 'STEAM 1,2',
	'total_block_fg': 'FG',
	'total_block_rpm': 'RPM',
	'total_block_lb': 'LABEL',
	'total_block': 'BLOCK 200',
	'total_fg': 'TOTAL FG',
	'total_pm': 'TOTAL PM',
	'total_rm': 'NORM. RM',
	'total_bdfg': 'FG BD 2500',
	'total_bdpm': 'PM PLT 4500',
	'total_mixup': 'MIXUP',
	'total_combinebin': 'COMBINE',
	'total_emptybin': 'EMPTY BIN'
}
	DICT_TITLE = {
			'wh1_total': f"WH1 CU:",
			'wh2_total': f"WH2 CU:",
			'wh3_total': f"WH3 CU:",
			'cool_total': f"COOLING:",
			'pf_total': f"PERFUME:",
			'label_total': f"WH LABEL:",
			'eo_total': f"EO & CONS:",
			'wh_total': f"BDWH#123(Ex EO,Cons):"
		}
	def __init__(self, varcontainer: VarContainerDrivative):
		self.varcontainer = varcontainer
	
	def get_gauge_configs(self) -> list[GaugeConfig]:
		configs: list[GaugeConfig] = []
		for field in fields(self.varcontainer):
			title = None
			height = None
			field_name = field.name
			field_value = getattr(self.varcontainer, field_name)
			metadata = field.metadata
			if metadata.get('chart_type') == 'gauge':
				name_split = field.name.split("_")
				wh_name = name_split[0]
				wh_level = name_split[1]
				capacity = self.CAPACITY_WAREHOUSE.get(wh_name, {}).get(wh_level, 0)
				if metadata.get('chart_title'):
					title = f"{self.DICT_TITLE.get(field.name)} {field_value/capacity:.0%}"
				if metadata.get('chart_height'):
					height = 110
				configs.append(GaugeConfig(name=field_name, title=title, value=field_value, capacity=capacity, height=height))
		return configs
	
	def get_metric_configs(self) -> list[MetricConfig]:
		configs: list[MetricConfig] = []
		for field in fields(self.varcontainer):
			title = None
			field_name = field.name
			field_value = getattr(self.varcontainer, field_name)
			metadata = field.metadata
			if metadata.get('chart_type') == 'metric':
				if metadata.get('chart_title'):
					title = self.TITLE_METRIC_CHART.get(field_name, '')
					if field_name.startswith('cool'):
						title = f"{title}{self.CAPACITY_WAREHOUSE.get('cool', {}).get(field_name)}"
					elif field_name.startswith('pf'):
						title = f"{title}{self.CAPACITY_WAREHOUSE.get('pf', {}).get(field_name)}"
					configs.append(MetricConfig(name=field_name, value=field_value, title=title))
		return configs
	
	def render_chart(self) ->DictChartTypeHint:
		list_gauge_configs = self.get_gauge_configs()
		list_metric_configs = self.get_metric_configs()
		dict_charts: Dict[str, Any] = {}
		for gauge in list_gauge_configs:
			fig = GaugeChart(title=gauge.title, value=gauge.value, capa=gauge.capacity, height=gauge.height).create_fig()
			dict_charts[gauge.name] = fig
		for metric in list_metric_configs:
			fig = Metric(label=metric.title, value=metric.value).create_metric_card()
			dict_charts[metric.name] = fig
		
		# obj_all_chart = DictChartTypeHint(**dict_charts)
		return  DictChartTypeHint(**dict_charts)
	



	



	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	