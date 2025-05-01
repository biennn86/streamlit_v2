from models.ChartModel import *
from models.AggregateDataModel import *
import re

class DashBoardModel:
    '''
    Trả về số pallet tầng vị trí của từng kho từ df tồn kho lấy từ class ImportInvTonDf
    '''
    def __init__(self, dfInv):
        self.dfInv = dfInv
        # try:
        #     self.obj_dftonkho = ImportInvToDf().ImportInv()
        #     self.dfInv = self.obj_dftonkho.mainReadTonkho()
        #     if self.dfInv is not None:
        #         self.StringDataTime = self.dfInv.iloc[0, 0]
        # except Exception as err:
        #     print('error cls countpldetailloc: ' + str(err))
        #     print('File Import Không Tồn Tại!')

        self.CAT = ('eo', 'fg', 'rpm')

    # def GetEmptyLoc(self):
    #     self.df_emptyloc = self.obj_dftonkho.emptyloc()
    #     return self.df_emptyloc
    # def GetCombinebin(self):
    #     self.df_combinebin = self.obj_dftonkho.combinebin()
    #     return self.df_combinebin
    # def GetMixup(self):
    #     self.df_mixup = self.obj_dftonkho.binmixup()
    #     return self.df_mixup
    # def GetInventory(self):
    #     self.df_inv = self.obj_dftonkho.get_inv()
    #     return self.df_inv

    def GetPl_Wh1(self):
        typelocwh1 = ('hr', 'pf', 'ww', 'in')
        namewh = 'wh1'
        dict_capa_wh1 = {
            'total': 1215,
            'hr': 966,
            'pf': 207,
            'fl': 42,
        }
        self.wh1_hr_eo = BaseCountPallet(self.dfInv, namewh, typelocwh1[0], self.CAT[0]).CountDetailLoc()
        self.wh1_hr_fg = BaseCountPallet(self.dfInv, namewh, typelocwh1[0], self.CAT[1]).CountDetailLoc()
        self.wh1_hr_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh1[0], self.CAT[2]).CountDetailLoc()

        self.wh1_pf_eo = BaseCountPallet(self.dfInv, namewh, typelocwh1[1], self.CAT[0]).CountDetailLoc()
        self.wh1_pf_fg = BaseCountPallet(self.dfInv, namewh, typelocwh1[1], self.CAT[1]).CountDetailLoc()
        self.wh1_pf_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh1[1], self.CAT[2]).CountDetailLoc()

        self.wh1_ww_eo = BaseCountPallet(self.dfInv, namewh, typelocwh1[2], self.CAT[0]).CountDetailLoc()
        self.wh1_ww_fg = BaseCountPallet(self.dfInv, namewh, typelocwh1[2], self.CAT[1]).CountDetailLoc()
        self.wh1_ww_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh1[2], self.CAT[2]).CountDetailLoc()

        self.wh1_in_eo = BaseCountPallet(self.dfInv, namewh, typelocwh1[3], self.CAT[0]).CountDetailLoc()
        self.wh1_in_fg = BaseCountPallet(self.dfInv, namewh, typelocwh1[3], self.CAT[1]).CountDetailLoc()
        self.wh1_in_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh1[3], self.CAT[2]).CountDetailLoc()

        self.wh1_floor = (self.wh1_ww_eo +
                          self.wh1_ww_fg +
                          self.wh1_ww_rpm +
                          self.wh1_in_eo +
                          self.wh1_in_fg +
                          self.wh1_in_rpm)
                          
        self.wh1_pf = (self.wh1_pf_fg +
                       self.wh1_pf_rpm +
                       self.wh1_pf_eo)
        
        self.wh1_hr = (self.wh1_hr_fg +
                       self.wh1_hr_rpm +
                       self.wh1_hr_eo)
        
        self.wh1_total = (self.wh1_floor +
                          self.wh1_pf +
                          self.wh1_hr)


        self.fig_wh1_total = CreateGauge('', self.wh1_total, dict_capa_wh1['total']).create_gauge()
        self.cu = f"{self.wh1_total/dict_capa_wh1['total']: .0%}"

        self.fig_wh1_hr = CreateGauge('', self.wh1_hr, dict_capa_wh1['hr']).create_gauge()

        self.fig_wh1_pf = CreateGauge('', self.wh1_pf, dict_capa_wh1['pf']).create_gauge()

        self.fig_wh1_fl = CreateGauge('', self.wh1_floor, dict_capa_wh1['fl']).create_gauge()

        dictfig_wh1 = {
            'total': self.fig_wh1_total,
            'hr': self.fig_wh1_hr,
            'pf': self.fig_wh1_pf,
            'fl': self.fig_wh1_fl,
            'cu': self.cu
        }

        return dictfig_wh1
    
    def GetPl_Wh2(self):
        '''
        Kho 2 có những vị trí đặc biệt và cách tính toán khác với wh1, wh2
        Điểm chung tính total pallet hightrack, level A và Floor
        Điểm riêng:
        - High Rack kho 2 cộng luôn tồn tầng A, hight rack của rack DA, trừ số pallet các vị trí HO
        - Floor: lấy tồn pallet các vị trí in (nhập 2,3,4), pick (fill hàng), các vị trí đường luồng wh2_
        các vị trí STJP, FGDM, FGLS
        Lưu ý: khi tính tồn kho hr, pf của wh2 đã có tồn kho của rack DA rồi. Nên chỉ cần lấy tồn pf_da trừ khỏi pf_wh2
        và cộng ngược lại hr_wh để đảm bảo tồn rack DA được cộng hết cho hr_wh2
        '''
        typelocwh2 = ('hr', 'pf', 'ww', 'in', 'pick', 'rework', 'return', 'scanout')
        namewh = 'wh2'
        dict_capa_wh2 = {
            'total': 5082,
            'hr': 4068,
            'pf': 758,
            'fl': 256,
        }
        self.wh2_hr_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[0], self.CAT[0]).CountDetailLoc()
        self.wh2_hr_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[0], self.CAT[1]).CountDetailLoc()
        self.wh2_hr_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[0], self.CAT[2]).CountDetailLoc()

        self.wh2_pf_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[1], self.CAT[0]).CountDetailLoc()
        self.wh2_pf_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[1], self.CAT[1]).CountDetailLoc()
        self.wh2_pf_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[1], self.CAT[2]).CountDetailLoc()

        self.wh2_ww_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[2], self.CAT[0]).CountDetailLoc()
        self.wh2_ww_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[2], self.CAT[1]).CountDetailLoc()
        self.wh2_ww_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[2], self.CAT[2]).CountDetailLoc()

        self.wh2_in_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[3], self.CAT[0]).CountDetailLoc()
        self.wh2_in_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[3], self.CAT[1]).CountDetailLoc()
        self.wh2_in_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[3], self.CAT[2]).CountDetailLoc()

        self.wh2_pick_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[4], self.CAT[0]).CountDetailLoc()
        self.wh2_pick_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[4], self.CAT[1]).CountDetailLoc()
        self.wh2_pick_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[4], self.CAT[2]).CountDetailLoc()

        self.wh2_rw_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[5], self.CAT[0]).CountDetailLoc()
        self.wh2_rw_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[5], self.CAT[1]).CountDetailLoc()
        self.wh2_rw_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[5], self.CAT[2]).CountDetailLoc()

        self.wh2_rt_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[6], self.CAT[0]).CountDetailLoc()
        self.wh2_rt_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[6], self.CAT[1]).CountDetailLoc()
        self.wh2_rt_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[6], self.CAT[2]).CountDetailLoc()

        self.wh2_scanout_eo = BaseCountPallet(self.dfInv, namewh, typelocwh2[7], self.CAT[0]).CountDetailLoc()
        self.wh2_scanout_fg = BaseCountPallet(self.dfInv, namewh, typelocwh2[7], self.CAT[1]).CountDetailLoc()
        self.wh2_scanout_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh2[7], self.CAT[2]).CountDetailLoc()

        '''
        Tính riêng tồn kho của rack DA và bin HO.
        Tồn rack DA sẽ được cộng vào tầng cao của WH2
        Tồn HO sẽ được cộng vào Floor của WH2
        '''
        typerack_da = ('hr', 'pf')
        typeloc_da = ('ob',)
        typerack_ho = ('pf',)
        typeloc_ho = ('ho',)

        self.wh2_hr_da_eo = CountPalletDAHO(self.dfInv, namewh, typerack_da[0], self.CAT[0], typeloc_da[0]).CountDetailLoc_DAHO()
        self.wh2_hr_da_fg = CountPalletDAHO(self.dfInv, namewh, typerack_da[0], self.CAT[1], typeloc_da[0]).CountDetailLoc_DAHO()
        self.wh2_hr_da_fpm = CountPalletDAHO(self.dfInv, namewh, typerack_da[0], self.CAT[2], typeloc_da[0]).CountDetailLoc_DAHO()

        self.wh2_pf_da_eo = CountPalletDAHO(self.dfInv, namewh, typerack_da[1], self.CAT[0], typeloc_da[0]).CountDetailLoc_DAHO()
        self.wh2_pf_da_fg = CountPalletDAHO(self.dfInv, namewh, typerack_da[1], self.CAT[1], typeloc_da[0]).CountDetailLoc_DAHO()
        self.wh2_pf_da_fpm = CountPalletDAHO(self.dfInv, namewh, typerack_da[1], self.CAT[2], typeloc_da[0]).CountDetailLoc_DAHO()

        self.wh2_pf_ho_eo = CountPalletDAHO(self.dfInv, namewh, typerack_ho[0], self.CAT[0], typeloc_ho[0]).CountDetailLoc_DAHO()
        self.wh2_pf_ho_fg = CountPalletDAHO(self.dfInv, namewh, typerack_ho[0], self.CAT[1], typeloc_ho[0]).CountDetailLoc_DAHO()
        self.wh2_pf_ho_fpm = CountPalletDAHO(self.dfInv, namewh, typerack_ho[0], self.CAT[2], typeloc_ho[0]).CountDetailLoc_DAHO()

        self.wh2_hr_da =  self.wh2_hr_da_eo + self.wh2_hr_da_fg + self.wh2_hr_da_fpm
        self.wh2_pf_da = self.wh2_pf_da_eo + self.wh2_pf_da_fg + self.wh2_pf_da_fpm

        self.wh2_pf_ho = self.wh2_pf_ho_eo + self.wh2_pf_ho_fg + self.wh2_pf_ho_fpm

        #=============================================================================
        self.wh2_rw = (self.wh2_rw_eo + self.wh2_rw_fg + self.wh2_rw_rpm)
        self.wh2_rt = (self.wh2_rt_eo + self.wh2_rt_fg + self.wh2_rt_rpm)
        self.wh2_ww = (self.wh2_ww_eo + self.wh2_ww_fg + self.wh2_ww_rpm)
        self.wh2_in = (self.wh2_in_eo + self.wh2_in_fg + self.wh2_in_rpm)
        self.wh2_pick = (self.wh2_pick_eo + self.wh2_pick_fg + self.wh2_pick_rpm)
        self.wh2_scanout = (self.wh2_scanout_eo + self.wh2_scanout_fg + self.wh2_scanout_rpm)

        self.wh2_floor = (self.wh2_rw + 
                          self.wh2_rt +
                          self.wh2_ww +
                          self.wh2_in + 
                          self.wh2_pick +
                          self.wh2_pf_ho
                          )
        
        self.wh2_pf = (self.wh2_pf_fg +
                       self.wh2_pf_rpm +
                       self.wh2_pf_eo -
                       self.wh2_pf_ho -
                       self.wh2_pf_da)
        
        self.wh2_hr = (self.wh2_hr_fg +
                       self.wh2_hr_rpm +
                       self.wh2_hr_eo + 
                       self.wh2_pf_da)
        
        self.wh2_total = (self.wh2_floor +
                          self.wh2_pf +
                          self.wh2_hr)


        self.fig_wh2_total = CreateGauge('', self.wh2_total, dict_capa_wh2['total']).create_gauge()
        self.cu = f"{self.wh2_total/dict_capa_wh2['total']: .0%}"

        self.fig_wh2_hr = CreateGauge('', self.wh2_hr, dict_capa_wh2['hr']).create_gauge()

        self.fig_wh2_pf = CreateGauge('', self.wh2_pf, dict_capa_wh2['pf']).create_gauge()

        self.fig_wh2_fl = CreateGauge('', self.wh2_floor, dict_capa_wh2['fl']).create_gauge()

        dictfig_wh2 = {
            'total': self.fig_wh2_total,
            'hr': self.fig_wh2_hr,
            'pf': self.fig_wh2_pf,
            'fl': self.fig_wh2_fl,
            'cu': self.cu
        }

        return dictfig_wh2

    def GetPl_Wh3(self):
        typelocwh3 = ('hr', 'pf', 'ww', 'in')
        namewh = 'wh3'
        dict_capa_wh3 = {
            'total': 2479,
            'hr': 2114,
            'pf': 343,
            'fl': 22,
        }
        self.wh3_hr_eo = BaseCountPallet(self.dfInv, namewh, typelocwh3[0], self.CAT[0]).CountDetailLoc()
        self.wh3_hr_fg = BaseCountPallet(self.dfInv, namewh, typelocwh3[0], self.CAT[1]).CountDetailLoc()
        self.wh3_hr_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh3[0], self.CAT[2]).CountDetailLoc()

        self.wh3_pf_eo = BaseCountPallet(self.dfInv, namewh, typelocwh3[1], self.CAT[0]).CountDetailLoc()
        self.wh3_pf_fg = BaseCountPallet(self.dfInv, namewh, typelocwh3[1], self.CAT[1]).CountDetailLoc()
        self.wh3_pf_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh3[1], self.CAT[2]).CountDetailLoc()

        self.wh3_ww_eo = BaseCountPallet(self.dfInv, namewh, typelocwh3[2], self.CAT[0]).CountDetailLoc()
        self.wh3_ww_fg = BaseCountPallet(self.dfInv, namewh, typelocwh3[2], self.CAT[1]).CountDetailLoc()
        self.wh3_ww_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh3[2], self.CAT[2]).CountDetailLoc()

        self.wh3_in_eo = BaseCountPallet(self.dfInv, namewh, typelocwh3[3], self.CAT[0]).CountDetailLoc()
        self.wh3_in_fg = BaseCountPallet(self.dfInv, namewh, typelocwh3[3], self.CAT[1]).CountDetailLoc()
        self.wh3_in_rpm = BaseCountPallet(self.dfInv, namewh, typelocwh3[3], self.CAT[2]).CountDetailLoc()

        '''
        WH3 floor có cộng thêm hàng EO ở dưới sàn
        Trên rack chưa cộng EO vào
        Nhưng không cộng tồn EO dưới sàn vào tổng tồn WH3
        '''
       
        self.wh3_floor = (self.wh3_ww_fg +
                          self.wh3_ww_rpm +
                          self.wh3_ww_eo +
                          self.wh3_in_eo +
                          self.wh3_in_fg +
                          self.wh3_in_rpm)
        
        self.wh3_pf = (self.wh3_pf_fg +
                       self.wh3_pf_rpm)
        
        self.wh3_hr = (self.wh3_hr_fg +
                       self.wh3_hr_rpm)
        
        self.wh3_total = (self.wh3_floor +
                          self.wh3_pf +
                          self.wh3_hr -
                          self.wh3_ww_eo -
                          self.wh3_in_eo)


        self.fig_wh3_total = CreateGauge('', self.wh3_total, dict_capa_wh3['total']).create_gauge()
        self.cu = f"{self.wh3_total/dict_capa_wh3['total']: .0%}"

        self.fig_wh3_hr = CreateGauge('', self.wh3_hr, dict_capa_wh3['hr']).create_gauge()

        self.fig_wh3_pf = CreateGauge('', self.wh3_pf, dict_capa_wh3['pf']).create_gauge()

        self.fig_wh3_fl = CreateGauge('', self.wh3_floor, dict_capa_wh3['fl']).create_gauge()

        dictfig_wh3 = {
            'total': self.fig_wh3_total,
            'hr': self.fig_wh3_hr,
            'pf': self.fig_wh3_pf,
            'fl': self.fig_wh3_fl,
            'cu': self.cu
        }

        return dictfig_wh3
    
    def GetPl_Lsl(self):
        typeloc_lsl = ('in', 'lslpm', 'lslrm', 'lrt')
        namewh = 'LSL'

        self.lsl_in_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[0], self.CAT[0]).CountDetailLoc()
        self.lsl_in_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[0], self.CAT[1]).CountDetailLoc()
        self.lsl_in_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[0], self.CAT[2]).CountDetailLoc()

        self.lsl_pm_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[1], self.CAT[0]).CountDetailLoc()
        self.lsl_pm_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[1], self.CAT[1]).CountDetailLoc()
        self.lsl_pm_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[1], self.CAT[2]).CountDetailLoc()

        self.lsl_rm_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[2], self.CAT[0]).CountDetailLoc()
        self.lsl_rm_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[2], self.CAT[1]).CountDetailLoc()
        self.lsl_rm_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[2], self.CAT[2]).CountDetailLoc()

        self.lsl_lrt_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[3], self.CAT[0]).CountDetailLoc()
        self.lsl_lrt_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[3], self.CAT[1]).CountDetailLoc()
        self.lsl_lrt_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lsl[3], self.CAT[2]).CountDetailLoc()

        self.lsl_in = (self.lsl_in_eo +
                       self.lsl_in_fg +
                       self.lsl_in_rpm)
        self.lsl_pm = (self.lsl_pm_eo +
                       self.lsl_pm_fg +
                       self.lsl_pm_rpm)
        self.lsl_rm = (self.lsl_rm_eo +
                       self.lsl_rm_fg +
                       self.lsl_rm_rpm)
        self.lsl_lrt = (self.lsl_lrt_eo +
                        self.lsl_lrt_fg +
                        self.lsl_lrt_rpm)
        self.obj_lsl_in = StMetric(label='PL EOL', value=self.lsl_in)
        self.obj_lsl_pm = StMetric(label='LSL PM', value=self.lsl_pm)
        self.obj_lsl_rm = StMetric(label='LSL RM', value=self.lsl_rm)
        self.obj_lsl_lrt = StMetric(label='LRT', value=self.lsl_lrt)

        self.dict_mt_lsl = {
            'pleol': self.obj_lsl_in,
            'lslpm': self.obj_lsl_pm,
            'lslrm': self.obj_lsl_rm,
            'lrt': self.obj_lsl_lrt
        }

        return self.dict_mt_lsl

    def GetPl_LB(self):
        typeloc_lb = ('hr', 'pf', 'ww')
        namewh = 'lb'
        dict_capa_lb = {
            'total': 1156
        }

        self.lb_hr_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lb[0], self.CAT[0]).CountDetailLoc()
        self.lb_hr_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lb[0], self.CAT[1]).CountDetailLoc()
        self.lb_hr_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lb[0], self.CAT[2]).CountDetailLoc()

        self.lb_pf_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lb[1], self.CAT[0]).CountDetailLoc()
        self.lb_pf_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lb[1], self.CAT[1]).CountDetailLoc()
        self.lb_pf_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lb[1], self.CAT[2]).CountDetailLoc()

        self.lb_ww_eo = BaseCountPallet(self.dfInv, namewh, typeloc_lb[2], self.CAT[0]).CountDetailLoc()
        self.lb_ww_fg = BaseCountPallet(self.dfInv, namewh, typeloc_lb[2], self.CAT[1]).CountDetailLoc()
        self.lb_ww_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_lb[2], self.CAT[2]).CountDetailLoc()

        self.lb_hr = (self.lb_hr_eo +
                      self.lb_hr_fg +
                      self.lb_hr_rpm)
        
        self.lb_pf = (self.lb_pf_eo +
                      self.lb_pf_fg +
                      self.lb_pf_rpm)
        
        self.lb_ww = (self.lb_ww_eo + 
                      self.lb_ww_fg + 
                      self.lb_ww_rpm)
        
        self.lb_total = (self.lb_hr +
                         self.lb_pf +
                         self.lb_ww)
        
        self.fig_lb = CreateGauge('', self.lb_total, dict_capa_lb['total']).create_gauge()
        self.cu = f"{self.lb_total/dict_capa_lb['total']: .0%}"

        dictfig_lb = {
            'total': self.fig_lb,
            'cu': self.cu
        }

        return dictfig_lb
    
    def GetPl_Cooling(self):
        dict_capa_cooling = {'total': 376}
        typeloc_cool = ('mk', 'ww')
        namewh = ('cool1', 'cool2', 'cool3')

        self.cool1_fl_eo = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[0], self.CAT[0]).CountDetailLoc()
        self.cool1_fl_fg = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[0], self.CAT[1]).CountDetailLoc()
        self.cool1_fl_rpm = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[0], self.CAT[2]).CountDetailLoc()
        self.cool1_ww_eo = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[1], self.CAT[0]).CountDetailLoc()
        self.cool1_ww_fg = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[1], self.CAT[1]).CountDetailLoc()
        self.cool1_ww_rpm = BaseCountPallet(self.dfInv, namewh[0], typeloc_cool[1], self.CAT[2]).CountDetailLoc()

        self.cool2_fl_eo = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[0], self.CAT[0]).CountDetailLoc()
        self.cool2_fl_fg = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[0], self.CAT[1]).CountDetailLoc()
        self.cool2_fl_rpm = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[0], self.CAT[2]).CountDetailLoc()
        self.cool2_ww_eo = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[1], self.CAT[0]).CountDetailLoc()
        self.cool2_ww_fg = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[1], self.CAT[1]).CountDetailLoc()
        self.cool2_ww_rpm = BaseCountPallet(self.dfInv, namewh[1], typeloc_cool[1], self.CAT[2]).CountDetailLoc()

        self.cool3_fl_eo = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[0], self.CAT[0]).CountDetailLoc()
        self.cool3_fl_fg = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[0], self.CAT[1]).CountDetailLoc()
        self.cool3_fl_rpm = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[0], self.CAT[2]).CountDetailLoc()
        self.cool3_ww_eo = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[1], self.CAT[0]).CountDetailLoc()
        self.cool3_ww_fg = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[1], self.CAT[1]).CountDetailLoc()
        self.cool3_ww_rpm = BaseCountPallet(self.dfInv, namewh[2], typeloc_cool[1], self.CAT[2]).CountDetailLoc()

        self.cool1_total = (self.cool1_fl_eo +
                            self.cool1_fl_fg +
                            self.cool1_fl_rpm
                            )
        
        self.cool2_total = (self.cool2_fl_eo + 
                            self.cool2_fl_fg +
                            self.cool2_fl_rpm
                            )
        
        self.cool3_total = (self.cool3_fl_eo + 
                            self.cool3_fl_fg +
                            self.cool3_fl_rpm
                            )
        
        self.cool_ww = (self.cool1_ww_eo + 
                        self.cool1_ww_fg + 
                        self.cool1_ww_rpm + 
                        self.cool2_ww_eo + 
                        self.cool2_ww_fg +
                        self.cool2_ww_rpm + 
                        self.cool3_ww_eo + 
                        self.cool3_ww_fg +
                        self.cool3_ww_rpm
                       )

        
        self.cool_total = (self.cool1_total + 
                           self.cool2_total + 
                           self.cool3_total + 
                            self.cool_ww)
        
        dict_mt_cool1 = StMetric(label='C1 - 96',
                            value = self.cool1_total,
                            )
        
        dict_mt_cool2 = StMetric(label='C2 - 178',
                            value = self.cool2_total,
                            )
        
        dict_mt_cool3 = StMetric(label='C3 - 126',
                            value = self.cool3_total,
                            )
        
        dict_mt_cool_ww = StMetric(label='Floor - 20',
                            value = self.cool_ww,
                            )
        
        self.fig_cool_total = CreateGauge('',  self.cool_total, dict_capa_cooling['total']).create_gauge()
        self.cu = f"{ self.cool_total/dict_capa_cooling['total']: .0%}"
        
        dict_cool_total = {
            'cool1': dict_mt_cool1,
            'cool2': dict_mt_cool2,
            'cool3': dict_mt_cool3,
            'cool_ww': dict_mt_cool_ww,
            'cool_total': self.fig_cool_total,
            'cu': self.cu
        }

        return dict_cool_total
    
    def GetPl_Perfume(self):
        dict_capa_pf = {'total': 364}
        typeloc_pf = ('mk', 'ww')
        namewh = ('pf1', 'pf2', 'pf3', 'pf4', 'pf5')

        self.pf1_fl_eo = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[0], self.CAT[0]).CountDetailLoc()
        self.pf1_fl_fg = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[0], self.CAT[1]).CountDetailLoc()
        self.pf1_fl_rpm = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[0], self.CAT[2]).CountDetailLoc()
        self.pf1_ww_eo = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[1], self.CAT[0]).CountDetailLoc()
        self.pf1_ww_fg = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[1], self.CAT[1]).CountDetailLoc()
        self.pf1_ww_rpm = BaseCountPallet(self.dfInv, namewh[0], typeloc_pf[1], self.CAT[2]).CountDetailLoc()

        self.pf2_fl_eo = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[0], self.CAT[0]).CountDetailLoc()
        self.pf2_fl_fg = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[0], self.CAT[1]).CountDetailLoc()
        self.pf2_fl_rpm = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[0], self.CAT[2]).CountDetailLoc()
        self.pf2_ww_eo = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[1], self.CAT[0]).CountDetailLoc()
        self.pf2_ww_fg = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[1], self.CAT[1]).CountDetailLoc()
        self.pf2_ww_rpm = BaseCountPallet(self.dfInv, namewh[1], typeloc_pf[1], self.CAT[2]).CountDetailLoc()

        self.pf3_fl_eo = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[0], self.CAT[0]).CountDetailLoc()
        self.pf3_fl_fg = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[0], self.CAT[1]).CountDetailLoc()
        self.pf3_fl_rpm = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[0], self.CAT[2]).CountDetailLoc()
        self.pf3_ww_eo = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[1], self.CAT[0]).CountDetailLoc()
        self.pf3_ww_fg = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[1], self.CAT[1]).CountDetailLoc()
        self.pf3_ww_rpm = BaseCountPallet(self.dfInv, namewh[2], typeloc_pf[1], self.CAT[2]).CountDetailLoc()

        self.pf4_fl_eo = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[0], self.CAT[0]).CountDetailLoc()
        self.pf4_fl_fg = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[0], self.CAT[1]).CountDetailLoc()
        self.pf4_fl_rpm = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[0], self.CAT[2]).CountDetailLoc()
        self.pf4_ww_eo = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[1], self.CAT[0]).CountDetailLoc()
        self.pf4_ww_fg = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[1], self.CAT[1]).CountDetailLoc()
        self.pf4_ww_rpm = BaseCountPallet(self.dfInv, namewh[3], typeloc_pf[1], self.CAT[2]).CountDetailLoc()

        self.pf5_fl_eo = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[0], self.CAT[0]).CountDetailLoc()
        self.pf5_fl_fg = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[0], self.CAT[1]).CountDetailLoc()
        self.pf5_fl_rpm = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[0], self.CAT[2]).CountDetailLoc()
        self.pf5_ww_eo = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[1], self.CAT[0]).CountDetailLoc()
        self.pf5_ww_fg = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[1], self.CAT[1]).CountDetailLoc()
        self.pf5_ww_rpm = BaseCountPallet(self.dfInv, namewh[4], typeloc_pf[1], self.CAT[2]).CountDetailLoc()

        self.pf1_total = (self.pf1_fl_eo + 
                          self.pf1_fl_fg +
                          self.pf1_fl_rpm)
        
        self.pf2_total = (self.pf2_fl_eo + 
                          self.pf2_fl_fg +
                          self.pf2_fl_rpm)
        
        self.pf3_total = (self.pf3_fl_eo + 
                          self.pf3_fl_fg +
                          self.pf3_fl_rpm)
        
        self.pf4_total = (self.pf4_fl_eo + 
                          self.pf4_fl_fg +
                          self.pf4_fl_rpm)
        
        self.pf5_total = (self.pf5_fl_eo +
                          self.pf5_fl_fg + 
                          self.pf5_fl_rpm)
        
        
        self.pf_ww_total = (self.pf1_ww_eo +
                            self.pf1_ww_fg +
                            self.pf1_ww_rpm + 
                            self.pf2_ww_eo +
                            self.pf2_ww_fg +
                            self.pf2_ww_rpm +
                            self.pf3_ww_eo +
                            self.pf3_ww_fg +
                            self.pf3_ww_rpm + 
                            self.pf4_ww_eo +
                            self.pf4_ww_fg +
                            self.pf4_ww_rpm +
                            self.pf5_ww_eo +
                            self.pf5_ww_fg +
                            self.pf5_ww_rpm)
        
        self.pf_total = (self.pf1_total +
                         self.pf2_total +
                         self.pf3_total +
                         self.pf4_total +
                         self.pf5_total +
                         self.pf_ww_total)
        
        dict_mt_pf1 = StMetric(
            label = 'PF1 - 32',
            value = self.pf1_total
        )

        dict_mt_pf2 = StMetric(
            label = 'PF2 - 42',
            value = self.pf2_total
        )

        dict_mt_pf3 = StMetric(
            label = 'PF3 - 36',
            value = self.pf3_total
        )

        dict_mt_pf4 = StMetric(
            label = 'PF4 - 66',
            value = self.pf4_total
        )

        dict_mt_pf5 = StMetric(
            label = 'PF5 - 188',
            value = self.pf5_total
        )

        dict_mt_pf_ww = StMetric(
            label = 'Floor - 37',
            value = self.pf_ww_total
        )

        self.fig_pf_total = CreateGauge('',  self.pf_total, dict_capa_pf['total']).create_gauge()
        self.cu = f"{ self.pf_total/dict_capa_pf['total']: .0%}"

        dict_pf_total = {
            'pf1': dict_mt_pf1,
            'pf2': dict_mt_pf2,
            'pf3': dict_mt_pf3,
            'pf4': dict_mt_pf4,
            'pf5': dict_mt_pf5,
            'pf_ww': dict_mt_pf_ww,
            'pf_total': self.fig_pf_total,
            'cu': self.cu
        }

        return dict_pf_total

    def GetPl_Steam(self):
        typeloc_steam = ('reject',)
        namewh = 'rej'

        self.steam_eo = BaseCountPallet(self.dfInv, namewh, typeloc_steam[0], self.CAT[0]).CountDetailLoc()
        self.steam_fg = BaseCountPallet(self.dfInv, namewh, typeloc_steam[0], self.CAT[1]).CountDetailLoc()
        self.steam_rpm = BaseCountPallet(self.dfInv, namewh, typeloc_steam[0], self.CAT[2]).CountDetailLoc()

        self.steam_total = (self.steam_eo + 
                            self.steam_fg +
                            self.steam_rpm)
        
        self.obj_mt_steam = StMetric(label='STEAM 1,2',
                            value = self.steam_total,
                            )
        
        self.dict_steam_total = {
            'steam': self.obj_mt_steam
        }

        return self.dict_steam_total

    def GetPl_Block(self):
        '''
        Tính tổng pallet block trừ vị trí stream có name_wh là REJ và EOL có name_wh LSL
        '''
        self.total_pallet_block = CountPalletBlock(self.dfInv).CountTotalPlBlock()
        self.pallet_fg_block = CountPalletBlock(self.dfInv).CountPlBlockFG()
        self.pallet_lb_block = CountPalletBlock(self.dfInv).CountPlBlockLB()
        self.pallet_rpm_block = self.total_pallet_block - self.pallet_fg_block - self.pallet_lb_block

        self.obj_mt_total_block = StMetric(label='BLOCK 200', value=self.total_pallet_block)
        self.obj_mt_fg_block = StMetric(label='FG', value=self.pallet_fg_block)
        self.obj_mt_rpm_block = StMetric(label='RPM', value=self.pallet_rpm_block)
        self.obj_mt_lb_block = StMetric(label='LABEL', value=self.pallet_lb_block)

        self.dict_mt_block = {
            'total_block': self.obj_mt_total_block,
            'fg_block': self.obj_mt_fg_block,
            'rpm_block': self.obj_mt_rpm_block,
            'lb_block': self.obj_mt_lb_block
        }

        return self.dict_mt_block

    def GetPl_Total_FG(self):
        '''
        Count tất cả pallet có cat_inv là FG. Tránh trường hợp count sót khi gcas chưa có trong masterdata
        Trừ đi FG ở cont, door (scanout) và trừ đi FG ở Steam
        '''
        

        cat_fg = 'FG'
        type1 = 'finished_goods'
        self.pallet_fg = CountPallet_FgRpmEo(self.dfInv, cat_fg).CoutPallet_Fg() - self.wh2_scanout_fg
        self.obj_mt_fg = StMetric(label='TOTAL FG', value=self.pallet_fg)

        self.dict_mt_fg = {
            'total_fg': self.obj_mt_fg
        }
        return self.dict_mt_fg
    
    def GetPl_FG(self):
        '''
        Tồn pallt FG phải từ thêm steam vì công thức lấy tồn FG là lấy hết những dòng có cat_inv là FG.
        Trong đó có cả những pallet ở steam, nên phải trừ ra.
        Tổng tồn trong wh1,2,3 từ đi hàng fg block

        '''
        #chạy method get steam trước. Vì khi tính totalwh(BDWH123) thì method GetPL_Steam chưa được gọi
        #method này đc gọi 2 lần :((
        # self.GetPl_Steam()
        self.fg_bd = self.pallet_fg - self.pallet_fg_block
        self.obj_fg_bd = StMetric(label='FG BD 2500', value=self.fg_bd)
        self.dict_fgbd = {
            'fg_bd': self.obj_fg_bd
        }
        return self.dict_fgbd
    
    def GetPl_Total_PM(self):
        #tính tổng cột pallet có cat_inv là rpm, type1 khác raw_mat ở trong name_wh (wh1, wh2. wh3)
        cat_rpm = 'RPM'
        type_not_pm = 'raw_mat'
        self.pallet_pm = CountPallet_FgRpmEo(self.dfInv, cat_rpm, type_not_pm).CoutPallet_Pm() - self.wh2_scanout_rpm
        self.obj_mt_pm = StMetric(label='TOTAL PM', value=self.pallet_pm)

        self.dict_mt_pm = {
            'total_pm': self.obj_mt_pm
        }
        return self.dict_mt_pm
    
    def GetPl_PM(self):
        #PM không trừ steam vì trong công thức lấy pallet rpm chỉ lấy trong wh1,2,3 mà steam ở kho rej.
        #Nghĩa là tồn pl rpm không có pl steam nên không cần trừ
        self.pm_plt = self.pallet_pm - self.pallet_rpm_block
        self.obj_rpm_plt = StMetric(label='PM PLT 4500', value=self.pm_plt)
        self.dict_pm_plt = {
            'pm_plt': self.obj_rpm_plt
        }
        return self.dict_pm_plt
    
    def GetPl_RM(self):
        #tính tổng cột pallet có cat_inv là rpm, type1 là raw_mat ở trong name_wh (wh1, wh2. wh3)
        cat_rpm = 'RPM'
        type_rm = 'raw_mat'
        self.pallet_rm = CountPallet_FgRpmEo(self.dfInv, cat_rpm, type_rm).CoutPallet_Rm()
        self.obj_mt_rm = StMetric(label='NORM. RM', value=self.pallet_rm)

        self.dict_mt_rm = {
            'rm': self.obj_mt_rm
        }
        return self.dict_mt_rm
    
    def GetPl_EO(self):
        #tính tổng cột pallet có cat_inv là EO
        self.dict_capa_eo = {'total': 546}
        cat_eo = 'EO'
        self.pallet_eo = CountPallet_FgRpmEo(self.dfInv, cat_eo).CoutPallet_Eo() - self.wh2_scanout_eo
        self.fig_eo = CreateGauge('', self.pallet_eo, self.dict_capa_eo['total']).create_gauge()
        self.cu = f"{self.pallet_eo/self.dict_capa_eo['total']: .0%}"

        self.dictfig_eo = {
            'total': self.fig_eo,
            'cu': self.cu
        }
        return self.dictfig_eo
    
    def GetPl_Total_BDWH(self):
        '''
        Lấy tổng tồn pallet FG, RPM của WH1,2,3 trừ đi pallet SCANOUT. 
        Mới: Không càn trừ scanout nữa vì đã trừ khi tính total FG
        '''
        self.dict_capa_total = {'total_pl': 8776}
        self.pl_fg = self.GetPl_Total_FG()['total_fg'].value
        self.pl_pm = self.GetPl_Total_PM()['total_pm'].value
        self.pl_rm = self.GetPl_RM()['rm'].value

        self.total_pallet_fgrpm = self.pl_fg + self.pl_pm +  self.pl_rm
        self.fig_total_fgrpm = CreateGauge('', self.total_pallet_fgrpm, self.dict_capa_total['total_pl']).create_gauge()
        self.cu = f"{self.total_pallet_fgrpm/self.dict_capa_total['total_pl']: .0%}"

        self.dictfig_total = {
            'total_pl': self.fig_total_fgrpm,
            'cu': self.cu
        }
        return  self.dictfig_total
    
    def GetPl_Scanout(self):
        '''
        Method này đang lấy kết quả của GetPl_Wh2. Sẽ không trả vè kết quả nếu hàm chưa được chạy
        '''
        self.pl_scanout = self.wh2_scanout
        self.obj_mt_scanout = StMetric(label='CONT**', value=self.pl_scanout)

        self.dict_mt_scanout = {
            'scanout': self.obj_mt_scanout
        }
        return self.dict_mt_scanout
    
    def GetPl_Fgls(self):
        loc = 'FGLS'
        self.pl_fgls = CountPalletWithLoc(self.dfInv, loc).CountPallet()
        self.obj_mt_fgls = StMetric('FGLS', self.pl_fgls)

        self.dict_mt_fgls = {
            'fgls': self.obj_mt_fgls
        }

        return self.dict_mt_fgls
    
    def GetPl_Fgdm(self):
        loc = 'FGDM'
        self.pl_fgdm = CountPalletWithLoc(self.dfInv, loc).CountPallet()
        self.obj_mt_fgdm = StMetric('FGDM', self.pl_fgdm)

        self.dict_mt_fgdm = {
            'fgdm': self.obj_mt_fgdm
        }

        return self.dict_mt_fgdm
    
    def GetPl_Matdm(self):
        loc = 'MATDM'
        self.pl_matdm = CountPalletWithLoc(self.dfInv, loc).CountPallet()
        self.obj_mt_matdm = StMetric('MATDM', self.pl_matdm)

        self.dict_mt_matdm = {
            'matdm': self.obj_mt_matdm
        }

        return self.dict_mt_matdm
    
    def GetPl_Lost(self):
        loc = 'LOST'
        self.pl_lost = CountPalletWithLoc(self.dfInv, loc).CountPallet()
        self.obj_mt_lost = StMetric('LOST', self.pl_lost)

        self.dict_mt_lost = {
            'lost': self.obj_mt_lost
        }

        return self.dict_mt_lost

    def GetPl_FgWithCat(self):
        #Count Pallet theo Cat dwn, febz, hdl dựa vào cat_inv và cat (masterdata)
        cat = ('dwn', 'febz', 'hdl')
        cat_inv = 'FG'
        self.total_pl_fg = CountPallet_FgRpmEo(self.dfInv, cat_inv).CoutPallet_Fg()

        self.pl_fg_dwn = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, cat_mtdata=cat[0]).Fg_Cat()
        self.pl_fg_febz = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, cat_mtdata=cat[1]).Fg_Cat()
        self.pl_fg_hdl = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, cat_mtdata=cat[2]).Fg_Cat()
        self.pl_fg_other = self.total_pl_fg - self.pl_fg_dwn - self.pl_fg_febz -self.pl_fg_hdl

        self.obj_mt_fgdwn = StMetric(label='FG DWN', value = self.pl_fg_dwn)
        self.obj_mt_fgfebz = StMetric(label='FG FEBZ', value=self.pl_fg_febz)
        self.obj_mt_fghdl = StMetric(label='FG HDL', value=self.pl_fg_hdl)
        self.obj_mt_fgother = StMetric(label='FG OTHER', value=self.pl_fg_other)

        self.dict_mt_fg_cat = {
            'fgdwn': self.obj_mt_fgdwn,
            'fgfebz': self.obj_mt_fgfebz,
            'fghdl': self.obj_mt_fghdl,
            'fgother': self.obj_mt_fgother
        }

        return self.dict_mt_fg_cat
    
    def GetPl_JIT(self):
        # jit = self.dfInv[self.dfInv['jit'] == 'JIT'].agg({'pallet': 'sum'})
        self.pallet_jit = CountPalletJIT(self.dfInv).PalletJIT()
        self.obj_mt_jit = StMetric(label='JIT', value = self.pallet_jit)
        self.dict_mt_jit = {
            'jit': self.obj_mt_jit
        }
        return self.dict_mt_jit
    
    def GetPl_PmWithCat(self):
        #Cout pallet theo cat_inv và type2 shipper, pouch, bottle
        cat = ('shipper', 'pouch', 'bottle')
        cat_inv = 'RPM'
        type_not_pm = 'raw_mat'
        
        self.total_pl_pm = CountPallet_FgRpmEo(self.dfInv, cat_inv, type_not_pm).CoutPallet_Pm()

        self.pl_pm_shipper = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, type2=cat[0]).Pm_Cat()
        self.pl_pm_pouch = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, type2=cat[1]).Pm_Cat()
        self.pl_pm_bottle = CountPalletWithCat(self.dfInv, cat_inv=cat_inv, type2=cat[2]).Pm_Cat()
        self.pl_pm_other = self.total_pl_pm - self.pl_pm_shipper - self.pl_pm_pouch - self.pl_pm_bottle

        self.obj_mt_pm_shipper = StMetric(label='SHIPPER', value=self.pl_pm_shipper)
        self.obj_mt_pm_pouch = StMetric(label='POUCH', value=self.pl_pm_pouch)
        self.obj_mt_pm_bottle = StMetric(label='BOTTLE', value=self.pl_pm_bottle)
        self.obj_mt_pm_other = StMetric(label='OTHER', value=self.pl_pm_other)


        self.dict_mt_pm_cat = {
            'shipper': self.obj_mt_pm_shipper,
            'pouch': self.obj_mt_pm_pouch,
            'bottle': self.obj_mt_pm_bottle,
            'other': self.obj_mt_pm_other
        }

        return self.dict_mt_pm_cat
    
    def GetPL_Mx_Combine_Emp(self):
        self.num_mixup = self.df_mixup['Location'].nunique()
        self.num_combinebin = self.df_combinebin.shape[0]
        self.df_combinebine_copy = self.df_emptyloc.copy()
        self.df_combinebine_copy.columns = [re.sub(r'[ -]', "_", string).lower() for string in self.df_combinebine_copy.columns]
        self.num_emploc_wh123 = self.df_combinebine_copy.query("(wh_name == 'WH1') | (wh_name == 'WH2') | (wh_name == 'WH3')").agg({'number_pallet': 'sum'})[0]

        self.obj_mt_num_mixup = StMetric(label='MIXUP', value=self.num_mixup)
        self.obj_mt_num_combinebin = StMetric(label='COMBINE', value=self.num_combinebin)
        self.obj_mt_num_emploc_wh123 = StMetric(label='EMPTY LOC', value=self.num_emploc_wh123)

        self.dict_mt_mx_com_emp = {
            'mixup': self.obj_mt_num_mixup,
            'combinebin': self.obj_mt_num_combinebin,
            'emploc_wh123': self.obj_mt_num_emploc_wh123
        }

        return self.dict_mt_mx_com_emp



    def Get_FgRpmEo_Total(self):
        '''
        chưa sử dụng
        '''
        wh1_fg = (self.wh1_hr_fg +
                  self.wh1_pf_fg +
                  self.wh1_ww_fg +
                  self.wh1_in_fg)
        
        wh2_fg = (self.wh2_hr_fg +
                  self.wh2_pf_fg +
                  self.wh2_ww_fg +
                  self.wh2_in_fg +
                  self.wh2_pick_fg +
                  self.wh2_rw_fg +
                  self.wh2_rt_fg +
                  self.wh2_scanout_fg)
        
        wh3_fg = (self.wh3_hr_fg +
                  self.wh3_pf_fg +
                  self.wh3_ww_fg +
                  self.wh3_in_fg)

        wh1_rpm = (self.wh1_hr_rpm +
                   self.wh1_pf_rpm +
                   self.wh1_ww_rpm +
                   self.wh1_in_rpm)
        
        wh2_rpm = (self.wh2_hr_rpm +
                   self.wh2_pf_rpm +
                   self.wh2_ww_rpm +
                   self.wh2_in_rpm)
        
        wh3_rpm = (self.wh3_hr_rpm +
                   self.wh3_pf_rpm +
                   self.wh3_ww_rpm +
                   self.wh3_in_rpm)

        wh1_eo = (self.wh1_hr_eo +
                  self.wh1_pf_eo +
                  self.wh1_ww_eo +
                  self.wh1_in_eo)
        
        wh2_eo = (self.wh2_hr_eo +
                  self.wh2_pf_eo +
                  self.wh2_ww_eo +
                  self.wh2_in_eo)
        
        wh3_eo = (self.wh3_hr_eo +
                  self.wh3_pf_eo +
                  self.wh3_ww_eo +
                  self.wh3_in_eo)

        self.total_fg = (wh1_fg +
                         wh2_fg +
                         wh3_fg)
        
        self.total_rpm = (wh1_rpm +
                          wh2_rpm +
                          wh3_rpm)
        
        self.total_eo = (wh1_eo +
                         wh2_eo +
                         wh3_eo)
        

        dict_total_fgrpmeo = {
            'fg': self.total_fg,
            'rpm': self.total_rpm,
            'eo': self.total_eo
        }

        return dict_total_fgrpmeo