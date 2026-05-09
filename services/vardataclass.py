from dataclasses import dataclass, field, fields

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
	# wh1_cu: int = field(init=False)
	
	def __post_init__(self):
		self.var_wh1()

	def var_wh1(self):
		self.wh1_floor = self.wh1_in_fg + self.wh1_in_rpm + self.wh1_in_eo + self.wh1_ww_fg + self.wh1_ww_rpm + self.wh1_ww_eo
		self.wh1_pf = self.wh1_pf_fg + self.wh1_pf_rpm + self.wh1_pf_eo
		self.wh1_hr = self.wh1_hr_fg + self.wh1_hr_rpm + self.wh1_hr_eo
		self.wh1_total = self.wh1_floor + self.wh1_pf + self.wh1_hr
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	