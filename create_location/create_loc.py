import pandas as pd
from controllers.location_new import *

class LocationMethod():
    def __init__(self, namerack, vitri, tang, category_rack, name_wh, note):
        self.namerack = namerack
        self.vitri = vitri
        self.tang = tang
        self.category_rack = category_rack
        self.name_wh = name_wh
        self.note = note

        if self.namerack.find('HO') != -1:
            self.namerack = self.namerack[2:]
            self.namerack_old = 'HO'
        else:
            self.namerack_old = self.namerack

    def category(self):
        self.ctgr = self.category_rack
        return self.ctgr
    
    def namewh(self):
        name_kho = self.name_wh
        return name_kho
    
    def type_rack(self):
        if self.name_wh == 'WH2' and self.tang[0] == 'A':
            type_r = 'PF'
        elif self.name_wh != 'WH2' and self.tang[0] == 'A':
            type_r = 'PF'
        elif self.tang[0] != 'A':
            type_r = 'HR'
        
        return  type_r
    
    def type_location(self):
        if (self.ctgr in ['DB']) and len(self.tang) == 2:
            self.type_loc = 'ST'
        elif self.namerack_old == 'HO':
            self.type_loc = 'HO'
        else:
            self.type_loc = self.ctgr
        return self.type_loc
    
    def name_rack(self):
        name_r = self.namerack_old
        return name_r
    
    def level(self):
        lv = self.tang[0]
        return lv
    
    def num_pallet(self):
        if self.ctgr == 'DB' and len(self.tang) == 1:
            num_pl = 2
        elif self.ctgr == 'OB' and self.tang[0] == 'A':
            num_pl = 4
        else:
            num_pl = 1
        return num_pl
    
    def stack_limit(self):
        #kho 2
        if self.ctgr == 'OB' and self.tang[0] == 'A':
            stack = 2
        else:
            stack = 1
        return stack
    
    def foorprint(self):
        if self.ctgr == 'OB' and self.tang[0] == 'A':
            foot = 8
        elif self.ctgr == 'DB' and len(self.tang) == 1:
            foot = 2
        else:
            foot = 1
        return foot
    
    def takenote(self):
        note = self.note.get(int(self.vitri), 'None')
        return note

class LocationMethodFloor():
    def __init__(self, location, type, category, type_loc, namewh, nameloc, level, pallet, stacklimit, footprint, note=None):
        self.location = location
        self.type = type
        self.category = category
        self.type_loc = type_loc
        self.namewh = namewh
        self.nameloc = nameloc
        self.level = level
        self.pallet = pallet
        self.stacklimit = stacklimit
        self.footprint = footprint
        self.note = note
        if self.note is None:
            self.note = 'None'

    def createlocfloor(self):
        noi = ';' 
        self.stringloc = self.location + noi + self.type + noi + self.category + noi + self.type_loc + noi +\
        self.namewh + noi + self.nameloc + noi + str(self.level) + noi + str(self.pallet) + noi + \
        str(self.stacklimit) + noi + str(self.footprint) + noi + self.note
        
        return self.stringloc

class CreateLocation():
    def __init__(self, namerack, vt_from, vt_to, tang, vt_ho, category_rack, name_wh, note):
        self.namerack = namerack
        self.vt_from = vt_from
        self.vt_to = vt_to
        self.tang = tang
        self.vt_ho = vt_ho
        self.category_rack = category_rack
        self.name_wh = name_wh
        self.note = note
            
    def create_loc(self):
        lst_loc = []
        for i in range(self.vt_from, self.vt_to):
            for tang in self.tang:
                if i in self.vt_ho and tang == 'A':
                    namerack = 'HO' + self.namerack
                    location = namerack + str(i).zfill(2)
                else:
                    namerack = self.namerack
                    location = namerack + str(i).zfill(2) + tang
                
                method_loc = LocationMethod(namerack, i, tang, self.category_rack, self.name_wh, self.note)
                ctgr = method_loc.category()
                type_r = method_loc.type_rack()
                type_loc = method_loc.type_location()
                namewh = method_loc.namewh()
                name_r = method_loc.name_rack()
                level = method_loc.level()
                num_pl = method_loc.num_pallet()
                stack = method_loc.stack_limit()
                foot = method_loc.foorprint()
                note = method_loc.takenote()
                string_location = location + ';' + type_r + ';' + ctgr + ';' +\
                      type_loc + ';' + namewh + ';' + name_r + ';' + level + ';' + \
                        str(num_pl) + ';' + str(stack) + ';' + str(foot) + ';' + note
                
                lst_loc.append(string_location)

        return lst_loc

def create_loc_wh2():
    CTGR_RACK_DB = 'DB'; CTGR_RACK_ST = 'ST'; CTGR_RACK_OB = 'OB'
    NAME_WH2 = 'WH2'
    name_rack_wh2 = ['FA', 'FB', 'FC', 'FD', 'FE', 'FF', 'FG', 'FH', 'FI', 'FK', 'FL', 'FM', 'DA']
    tang_fa = ['A', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E']
    tang_fd = ['A', 'B1', 'B2', 'C', 'D', 'E']
    tang_fd_eo = ['A', 'B', 'C', 'D', 'E']
    tang_ae = ['A', 'B', 'C', 'D', 'E']
    tang_af = ['A', 'B', 'C', 'D', 'E', 'F']
    tang_da = ['A', 'B1', "B2", 'C1', 'C2', 'D1', 'D2']
    tang_da_new = ['AN','AT', 'BN', 'BT', 'CN', 'CT', 'DN', 'DT']
    tang_fm = ['A', 'B', 'C1', 'C2', 'D1', 'D2', 'E']
    locwh2 = []
    for namerack in name_rack_wh2:
        if namerack in ['FA']:
            loc_fa = CreateLocation(namerack, 1, 32, tang_fa, [9, 10, 20, 21], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FB']:
            loc_fb = CreateLocation(namerack, 1, 34, tang_ae, [10, 11, 22, 23], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FC']:
            loc_fc = CreateLocation(namerack, 1, 35, tang_ae, [12, 13, 23, 24], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FD']:
            loc_fd = CreateLocation(namerack, 1, 33, tang_fd, [13, 14, 25, 26], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
            loc_fd_eo = CreateLocation(namerack, 33, 37, tang_fd_eo, [], CTGR_RACK_DB, NAME_WH2, {
                33: 'EO_BIN',
                34: 'EO_BIN',
                35: 'EO_BIN',
                36: 'EO_BIN'
            }).create_loc()
        elif namerack in ['FE']:
            loc_fe = CreateLocation(namerack, 1, 35, tang_af, [12, 13, 23, 24], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FF']:
            loc_ff = CreateLocation(namerack, 1, 37, tang_af, [13, 14, 25, 26], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FG']:
            loc_fg = CreateLocation(namerack, 1, 35, tang_af, [12, 13, 23, 24], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FH']:
            loc_fh = CreateLocation(namerack, 1, 37, tang_af, [13, 14, 25, 26], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FI']:
            loc_fi = CreateLocation(namerack, 1, 35, tang_af, [12, 13, 23, 24], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FK']:
            loc_fk = CreateLocation(namerack, 1, 37, tang_af, [13, 14, 25, 26], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FL']:
            loc_fl = CreateLocation(namerack, 1, 35, tang_ae, [12, 13, 23, 24], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack in ['FM']:
            loc_fm = CreateLocation(namerack, 1, 37, tang_fm, [13, 14, 25, 26], CTGR_RACK_DB, NAME_WH2, {}).create_loc()
        elif namerack == 'DA':
            # loc_da = CreateLocation(namerack, 1, 31, tang_da, [], CTGR_RACK_OB, NAME_WH2, {}).create_loc()
            loc_da_new = CreateLocation(namerack, 1, 31, tang_da_new, [], CTGR_RACK_OB, NAME_WH2, {}).create_loc()

    locwh2 = loc_fa + loc_fb + loc_fc + loc_fd + loc_fd_eo + loc_fe +\
            loc_ff + loc_fg + loc_fh + loc_fi + loc_fk +\
            loc_fl + loc_fm + loc_da + loc_da_new
    return locwh2

def create_loc_wh1():
    CATEGORY_DB = 'DB'; CATEGORY_ST = 'ST'
    NAME_WH1 = 'WH1'
    PCCC = 'BO_TANG_E_PCCC'; DNDC = 'TANG_A_LSL_LRT_DNDC'; CA = 'TANG_A_LSL_CA'
    WW = 'WW_MID_WH'
    rack_wh1 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
    tang_cd = ['C', 'D']
    tang_ad = ['A', 'B', 'C', 'D']
    tang_ae = ['A', 'B', 'C', 'D', 'E']
    tang_bd = ['B', 'C', 'D']
    tang_12 = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'F1', 'F2']
    tang_10 = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2']
    tang_8 =  ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2']
    tang_7 = ['A', 'B', 'C1', 'C2', 'D1', 'D2', 'E']
    tang_6 = ['A', 'B', 'C1', 'C2', 'D1', 'D2']
    locwh1 = []
    locb1 = []; locb2 = []; locb3 = []; locb4 = []; locb5 = []; locb6 = []; locb7 = []; locb8 = []
    
    for namerack in rack_wh1:
        if namerack in ['B1']:
            locb1_1 = CreateLocation(namerack, 2, 7, tang_bd, [], CATEGORY_DB, NAME_WH1, {
                2: DNDC,
                3: DNDC,
                4: DNDC,
                5: DNDC,
                6: DNDC
            }).create_loc()
            locb1_2 = CreateLocation(namerack, 7, 10, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                7: WW,
                8: WW,
                9: WW,
            }).create_loc()
            locb1_3 = CreateLocation(namerack, 10, 16, tang_bd, [], CATEGORY_DB, NAME_WH1, {
                10: DNDC,
                11: DNDC,
                12: DNDC,
                13: DNDC,
                14: DNDC,
                15: DNDC,
            }).create_loc()
            locb1_4 = CreateLocation(namerack, 17, 22, tang_bd, [], CATEGORY_DB, NAME_WH1, {
                17: CA,
                18: CA,
                19: CA,
                20: CA,
                21: CA,
            }).create_loc()
            locb1_5 = CreateLocation(namerack, 22, 25, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                22: WW,
                23: WW,
                24: WW,
            }).create_loc()
            locb1_6 = CreateLocation(namerack, 25, 31, tang_ad, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
           
            locb1 = locb1_1 + locb1_2 + locb1_3 + locb1_4 + locb1_5 + locb1_6
        elif namerack in ['B2']:
            locb2_1 = CreateLocation(namerack, 5, 7, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb2_2 = CreateLocation(namerack, 7, 10, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                7: WW,
                8: WW,
                9: WW,
            }).create_loc()
            locb2_3 = CreateLocation(namerack, 10, 14, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb2_4 = CreateLocation(namerack, 14, 18, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                14: PCCC,
                15: PCCC,
                16: PCCC,
                17: PCCC,
            }).create_loc()
            locb2_5 = CreateLocation(namerack, 18, 21, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb2_6 = CreateLocation(namerack, 21, 24, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                21: WW,
                22: WW,
                23: WW,
            }).create_loc()
            locb2_7 = CreateLocation(namerack, 24, 28, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb2_8 = CreateLocation(namerack, 28, 30, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                28: PCCC,
                29: PCCC,
            }).create_loc()

            locb2 = locb2_1 + locb2_2 + locb2_3 + locb2_4 + locb2_5 + locb2_6 + locb2_7 + locb2_8
        elif namerack in ['B3']:
            locb3_1 = CreateLocation(namerack, 1, 3, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                1: PCCC,
                2: PCCC,
            }).create_loc()
            locb3_2 = CreateLocation(namerack, 3, 6, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb3_3 = CreateLocation(namerack, 6, 9, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                6: WW,
                7: WW,
                8: WW,
            }).create_loc()
            locb3_4 = CreateLocation(namerack, 9, 13, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb3_5 = CreateLocation(namerack, 13, 17, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                13: PCCC,
                14: PCCC,
                15: PCCC,
                16: PCCC,
            }).create_loc()
            locb3_6 = CreateLocation(namerack, 17, 20, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb3_7 = CreateLocation(namerack, 20, 23, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                20: WW,
                21: WW,
                22: WW,
            }).create_loc()
            locb3_8 = CreateLocation(namerack, 23, 27, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb3_9 = CreateLocation(namerack, 27, 29, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                27: PCCC,
                28: PCCC,
                29: PCCC,
            }).create_loc()

            locb3 = locb3_1 + locb3_2 + locb3_3 + locb3_4 + locb3_5 + locb3_6 + locb3_7 + locb3_8 + locb3_9
        elif namerack in ['B4']:
            locb4_1 = CreateLocation(namerack, 1, 3, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                1: PCCC,
                2: PCCC,
            }).create_loc()
            locb4_2 = CreateLocation(namerack, 3, 6, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb4_3 = CreateLocation(namerack, 6, 9, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                6: WW,
                7: WW,
                8: WW,
            }).create_loc()
            locb4_4 = CreateLocation(namerack, 9, 13, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb4_5 = CreateLocation(namerack, 13, 15, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                13: PCCC,
                14: PCCC,
            }).create_loc()
            locb4_6 = CreateLocation(namerack, 15, 16, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb4_7 = CreateLocation(namerack, 16, 19, tang_cd, [], CATEGORY_DB, NAME_WH1, {
                16: WW,
                17: WW,
                18: WW,
            }).create_loc()
            locb4_8 = CreateLocation(namerack, 19, 23, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb4_9 = CreateLocation(namerack, 23, 25, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                23: PCCC,
                24: PCCC,
            }).create_loc()

            locb4 = locb4_1 + locb4_2 + locb4_3 + locb4_4 + locb4_5 + locb4_6 + locb4_7 + locb4_8 + locb4_9
        elif namerack in ['B5']:
            locb5_1 = CreateLocation(namerack, 5, 9, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb5_2 = CreateLocation(namerack, 9, 11, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                9: PCCC,
                10: PCCC,
            }).create_loc()
            locb5_3 = CreateLocation(namerack, 15, 19, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb5_4 = CreateLocation(namerack, 19, 21, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                19: PCCC,
                20: PCCC,
            }).create_loc()

            locb5 = locb5_1 + locb5_2 + locb5_3 + locb5_4
        elif namerack in ['B6']:
            locb6_1 = CreateLocation(namerack, 5, 9, tang_ae, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb6_2 = CreateLocation(namerack, 9, 11, tang_ad, [], CATEGORY_DB, NAME_WH1, {
                9: PCCC,
                10: PCCC,
            }).create_loc()
            locb6_3 = CreateLocation(namerack, 15, 19, tang_10, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb6_4 = CreateLocation(namerack, 19, 21, tang_8, [], CATEGORY_DB, NAME_WH1, {
                19: PCCC,
                20: PCCC,
            }).create_loc()

            locb6 = locb6_1 + locb6_2 + locb6_3 + locb6_4
        elif namerack in ['B7']:
            locb7_1 = CreateLocation(namerack, 5, 9, tang_ae, [], CATEGORY_ST, NAME_WH1, {}).create_loc()
            locb7_2 = CreateLocation(namerack, 9, 11, tang_ad, [], CATEGORY_ST, NAME_WH1, {
                9: PCCC,
                10: PCCC,
            }).create_loc()
            locb7_3 = CreateLocation(namerack, 15, 19, tang_ae, [], CATEGORY_ST, NAME_WH1, {}).create_loc()
            locb7_4 = CreateLocation(namerack, 19, 21, tang_ad, [], CATEGORY_ST, NAME_WH1, {
                19: PCCC,
                20: PCCC,
            }).create_loc()

            locb7 = locb7_1 + locb7_2 + locb7_3 + locb7_4
        elif namerack in ['B8']:
            locb8_1 = CreateLocation(namerack, 2, 9, tang_12, [], CATEGORY_DB, NAME_WH1, {}).create_loc()
            locb8_2 = CreateLocation(namerack, 9, 11, tang_10, [], CATEGORY_DB, NAME_WH1, {
                9: PCCC,
                10: PCCC,
            }).create_loc()

            locb8 = locb8_1 + locb8_2

    locwh1 = locb1 + locb2 + locb3 + locb4 + locb5 + locb6 + locb7 + locb8
    return locwh1

def create_loc_wh3():
    CTGR_RACK_DB = 'DB'; CTGR_RACK_ST = 'ST'; CTGR_RACK_SV = 'SV'
    NAME_WH3 = 'WH3'
    WW_K3 = 'WW_MID_WH'; VUONG_COT = 'VUONG_COT'; DAMAGE = 'BIN_DAMAGE'; SV_DAMAGE = 'BIN_SV_DAMAGE'; SV_LRT = 'BIN_SV_LRT'
    rackwh3 = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10']
    tang_ak = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K']
    tang_ah = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    tang_ag = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    tang_ae = ['A', 'B', 'C', 'D', 'E']
    tang_af = ['A', 'B', 'C', 'D', 'E', 'F']
    tang_dg = ['D', 'E', 'F', 'G']
    tang_ce = ['C', 'D', 'E']
    tang_a8 = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
    tang_11 = ['A', 'B', 'C1', 'C2', 'D1', 'D2', 'E1', 'E2', 'F1', 'F2', 'G']
    locwh3 = []
    locg1 = []; locg2 = []; locg3 = []; locg4 = []; locg5 = []; locg6 = []
    locg7 = []; locg8 = []; locg9 = []; locg10 = []

    for namerack in rackwh3:
        if namerack in ['G1']:
            lst_bin_sv = [i for i in range(15, 32)]
            locg1_1 = CreateLocation(namerack, 0, 32, tang_ak, [], CTGR_RACK_ST, NAME_WH3, {}).create_loc()
            locg1_2 = CreateLocation(namerack, 15, 32, tang_a8, [], CTGR_RACK_SV, NAME_WH3, {
                key: SV_LRT for key in lst_bin_sv
            }).create_loc()
            locg1 = locg1_1 + locg1_2
        elif namerack in ['G2']:
            locg2_1 = CreateLocation(namerack, 0, 32, tang_ah, [], CTGR_RACK_ST, NAME_WH3, {}).create_loc()
            locg2 = locg2_1
        elif namerack in ['G3']:
            locg3_1 = CreateLocation(namerack, 0, 35, tang_ag, [], CTGR_RACK_ST, NAME_WH3, {}).create_loc()
            locg3 = locg3_1
        elif namerack in ['G4']:
            locg4_1 = CreateLocation(namerack, 0, 35, tang_ag, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg4 = locg4_1
        elif namerack in ['G5']:
            locg5_1 = CreateLocation(namerack, 0, 18, tang_ae, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg5_2 = CreateLocation(namerack, 18, 21, tang_ce, [], CTGR_RACK_DB, NAME_WH3, {
                18: WW_K3,
                19: WW_K3,
                20: WW_K3
            }).create_loc()
            locg5_3 = CreateLocation(namerack, 21, 37, tang_ae, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg5 = locg5_1 + locg5_2 + locg5_3
        elif namerack in ['G6']:
            locg6_1 = CreateLocation(namerack, 0, 18, tang_ae, [], CTGR_RACK_DB, NAME_WH3, {
                4: VUONG_COT,
                10: VUONG_COT,
                16: VUONG_COT
            }).create_loc()
            locg6_2 = CreateLocation(namerack, 18, 21, tang_ce, [], CTGR_RACK_DB, NAME_WH3, {
                18: WW_K3,
                19: WW_K3,
                20: WW_K3
            }).create_loc()
            locg6_3 = CreateLocation(namerack, 21, 22, tang_ae, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg6 = locg6_1 + locg6_2 + locg6_3
        elif namerack in ['G7']:
            locg7_1 = CreateLocation(namerack, 0, 18, tang_11, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg7_2 = CreateLocation(namerack, 18, 21, tang_dg, [], CTGR_RACK_DB, NAME_WH3, {
                18: WW_K3,
                19: WW_K3,
                20: WW_K3
            }).create_loc()
            locg7_3 = CreateLocation(namerack, 21, 22, tang_ag, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg7 = locg7_1 + locg7_2 + locg7_3
        elif namerack in ['G8']:
            locg8_1 = CreateLocation(namerack, 0, 18, tang_ag, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg8_2 = CreateLocation(namerack, 18, 21, tang_dg, [], CTGR_RACK_DB, NAME_WH3, {
                18: WW_K3,
                19: WW_K3,
                20: WW_K3
            }).create_loc()
            locg8_3 = CreateLocation(namerack, 21, 22, tang_ag, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg8 = locg8_1 + locg8_2 + locg8_3
        elif namerack in ['G9']:
            locg9_1 = CreateLocation(namerack, 00, 13, tang_af, [], CTGR_RACK_DB, NAME_WH3, {}).create_loc()
            locg9 = locg9_1
        elif namerack in ['G10']:
            locg10_1 = CreateLocation(namerack, 00, 13, tang_af, [], CTGR_RACK_ST, NAME_WH3, {
                11: DAMAGE,
                12: DAMAGE
            }).create_loc()
            locg10_2 = CreateLocation(namerack, 11, 13, tang_a8, [], CTGR_RACK_SV, NAME_WH3, {
                11: SV_DAMAGE,
                12: SV_DAMAGE
            }).create_loc()
            locg10 = locg10_1 + locg10_2


    locwh3 = locg1 + locg2 + locg3 + locg4 + locg5 + locg6 + locg7 + locg8 + locg9 + locg10
    return locwh3

def create_loc_label_old():
    def create_level_lb(vitri, so_tang):
        tang_ac = ['A', 'B', 'C']
        tang_ad = ['A', 'B', 'C', 'D']
        tang_d = ['D']
        result = []
        if so_tang == 3:
            tang_label = tang_ac
        elif so_tang == 1:
            tang_label = tang_d
        else:
            tang_label = tang_ad

        for i in tang_label:
            for j in range(1, vitri + 1):
                tang = i+str(j)
                result.append(tang)
        return result
    
    rackwh_label = ['LB1', 'LB2', 'LB3', 'LB4', 'LB5', 'LB6', 'LB7']
    CTGR_RACK_SV = 'SV'; NAME_WH_LABEL = 'LB'
    loc_lb = []; loc_lb1 = []; loc_lb2 = []; loc_lb3 = []; loc_lb4 = []
    loc_lb5 = []; loc_lb6 = []; loc_lb7 = []
    for namerack in rackwh_label:
        if namerack in ['LB1']:
            loc_lb1_1 = CreateLocation(namerack, 1, 6, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb1_2 = CreateLocation(namerack, 6, 12, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb1 = loc_lb1_1 + loc_lb1_2
        elif namerack in ['LB2']:
            loc_lb2_1 = CreateLocation(namerack, 1, 9, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb2_2 = CreateLocation(namerack, 9, 17, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb2 = loc_lb2_1 + loc_lb2_2
        elif namerack in ['LB3']:
            loc_lb3_1 = CreateLocation(namerack, 1, 17, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3_2 = CreateLocation(namerack, 1, 17, create_level_lb(2, 1), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3_3 = CreateLocation(namerack, 17, 24, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3 = loc_lb3_1 + loc_lb3_2 + loc_lb3_3
        elif namerack in ['LB4']:
            loc_lb4_1 = CreateLocation(namerack, 1, 21, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb4_2 = CreateLocation(namerack, 21, 29, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb4 = loc_lb4_1 + loc_lb4_2
        elif namerack in ['LB5']:
            loc_lb5_1 = CreateLocation(namerack, 1, 21, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb5_2 = CreateLocation(namerack, 21, 28, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb5 = loc_lb5_1 + loc_lb5_2
        elif namerack in ['LB6']:
            loc_lb6_1 = CreateLocation(namerack, 1, 21, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb6_2 = CreateLocation(namerack, 21, 28, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb6 = loc_lb6_1 + loc_lb6_2
        elif namerack in ['LB7']:
            loc_lb7_1 = CreateLocation(namerack, 1, 17, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb7_2 = CreateLocation(namerack, 17, 24, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb7 = loc_lb7_1 + loc_lb7_2

    loc_lb = loc_lb1 + loc_lb2 + loc_lb3 + loc_lb4 + loc_lb5 + loc_lb6 + loc_lb7
    return loc_lb

def create_loc_label():
    def create_level_lb(vitri, so_tang):
        tang_ac = ['A', 'B', 'C']
        tang_ad = ['A', 'B', 'C', 'D']
        tang_d = ['D']
        result = []
        if so_tang == 3:
            tang_label = tang_ac
        elif so_tang == 1:
            tang_label = tang_d
        else:
            tang_label = tang_ad

        for i in tang_label:
            for j in range(1, vitri + 1):
                tang = i+str(j)
                result.append(tang)
        return result
    
    rackwh_label = ['LB3', 'LB4', 'LB5', 'LB6', 'LB7']
    CTGR_RACK_SV = 'SV'; NAME_WH_LABEL = 'LB'; NOTE_REJECT = 'LB_REJECT'; NOTE_EO = 'LB_EO'
    loc_lb = []; loc_lb3 = []; loc_lb4 = []
    loc_lb5 = []; loc_lb6 = []; loc_lb7 = []
    #nhập range vị trí đến thì cộng thêm 1
    for namerack in rackwh_label:
        if namerack in ['LB3']:
            loc_lb3_1 = CreateLocation(namerack, 1, 13, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3_2 = CreateLocation(namerack, 1, 13, create_level_lb(2, 1), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3_3 = CreateLocation(namerack, 17, 24, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb3 = loc_lb3_1 + loc_lb3_2 + loc_lb3_3
        elif namerack in ['LB4']:
            loc_lb4_1 = CreateLocation(namerack, 1, 21, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb4_2 = CreateLocation(namerack, 21, 29, create_level_lb(3, 3), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb4 = loc_lb4_1 + loc_lb4_2
        elif namerack in ['LB5']:
            loc_lb5_1 = CreateLocation(namerack, 1, 17, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb5_2 = CreateLocation(namerack, 21, 28, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb5 = loc_lb5_1 + loc_lb5_2
        elif namerack in ['LB6']:
            loc_lb6_1 = CreateLocation(namerack, 1, 21, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb6_2 = CreateLocation(namerack, 21, 28, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb6 = loc_lb6_1 + loc_lb6_2
        elif namerack in ['LB7']:
            loc_lb7_1 = CreateLocation(namerack, 1, 9, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            loc_lb7_2 = CreateLocation(namerack, 18, 24, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {}).create_loc()
            #vị tri label reject
            loc_lb7_reject = CreateLocation(namerack, 24, 25, create_level_lb(2, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {
                24: NOTE_REJECT
            }).create_loc()
            #vị trí eo
            loc_lb7_eo = CreateLocation(namerack, 17, 18, create_level_lb(3, 4), [], CTGR_RACK_SV, NAME_WH_LABEL, {
                17: NOTE_EO
            }).create_loc()
            loc_lb7 = loc_lb7_1 + loc_lb7_2 + loc_lb7_reject + loc_lb7_eo

    loc_lb = loc_lb3 + loc_lb4 + loc_lb5 + loc_lb6 + loc_lb7
    return loc_lb

def create_loc_floor():
    loc_fl = []
    level = 0
    #1 Sàn kho 1

    flin_wh1 = ['ST17', 'ST18', 'ST19']
    for loc in flin_wh1:
        loc_flin_wh1 = LocationMethodFloor(loc, 'IN', 'FL', 'FL', 'WH1', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_flin_wh1)
    #2 Vi trí xuất, pick kho 2
    flin_wh2 = ['ST01', 'ST02', 'ST03', 'ST04']
    for loc in flin_wh2:
        loc_flin_wh2 = LocationMethodFloor(loc, 'IN', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_flin_wh2)

    flout_wh2 = ['ST' + str(i).zfill(2) for i in range(5, 17)]
    for loc in flout_wh2:
        loc_flout_wh2 = LocationMethodFloor(loc, 'PICK', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_flout_wh2)

    flship_exw = ['EXW' + str(i) for i in range(1, 11)]
    flship_c = ['C' + str(i).zfill(3) for i in range(1, 201)]
    flship = flship_c + flship_exw
    for loc in flship:
        loc_flship = LocationMethodFloor(loc, 'SHIPOUT', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_flship)

    fl_door = ['DOOR' + str(i).zfill(2) for i in range(1, 101)]
    fl_cont = ['CONT' + str(i).zfill(3) for i in range(1, 101)]
    flscanout = fl_door + fl_cont
    for loc in flscanout:
        loc_flout = LocationMethodFloor(loc, 'SCANOUT', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_flout)
    #3 Vị trí cấp hàng xưởng
    lst_pm = 'DX,DC,DM,DJ,AU,DK,DQ,DV,DF,AE,AK,PD,AM,DD,DW,DZ,DV,FE,DN,JA,FX,FC,FD,FR,CA,AT,AA'.split(',')
    lsl_pm = ['PL' + i for i in set(lst_pm)]
    lst_xuongsx = ['ST' + i for i in set(lst_pm)]
    for loc in lsl_pm:
        loc_lslpm = LocationMethodFloor(loc, 'LSLPM', 'FL', 'FL', 'LSL', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_lslpm)
    #VT xưởng ra hàng FG
    for loc in lst_xuongsx:
        loc_xuongsx = LocationMethodFloor(loc, 'IN', 'FL', 'FL', 'LSL', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_xuongsx)

    lsl_rm = {'HO10', 'HO03', 'PLMA', 'PLMD', 'PLMF', 'PLMK'}
    for loc in lsl_rm:
        loc_lslrm = LocationMethodFloor(loc, 'LSLRM', 'FL', 'FL', 'LSL', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_lslrm)

    lrt = {'RTPD', 'RTMA', 'RTPA'}
    for loc in lrt:
        loc_lrt = LocationMethodFloor(loc, 'LRT', 'FL', 'FL', 'LSL', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_lrt)
    #4 Sàn kho 2
    w2w_wh2 = {'WH2FA', 'WH2FB', 'WH2FC', 'WH2FD', 'WH2FF', 'WH2FH', 'WH2FK', 'WH2FM', 'HOFA', 'HOFBFC', 'HOFDFF', 'HOFFFG', 'HOFHFI', 'HOFKFL', 'HOFMF9'}
    for loc in w2w_wh2:
        loc_w2wwh2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_w2wwh2)
    #5 Sàn kho 3
    w2w_wh3 = {'WH3G1', 'WH3G3', 'WH3G5', 'WH3G9', 'WH3G7', 'WH3G1G2', 'WH3G3G4', 'WH3G5G6', 'WH3G7G8', 'WH3ST15',
               'HOG2G3', 'HOG4G5', 'HOG8G9', 'HOG6G7', 'RJG10F'}
    for loc in w2w_wh3:
        loc_w2wwh3 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'WH3', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_w2wwh3)
    #6 Sàn kho 1
    w2w_wh1 = {'WH1B1', 'WH1B2', 'WH1B3', 'WH1B4', 'WH1B5', 'WH1B6', 'WH1B7', 'WH1B7', 'WH1L1', 'WHL1',
               'HOB1', 'HOB2', 'HOB3', 'HOB4', 'HOB5', 'HOB6', 'HOB7', 'HOB8'}
    for loc in w2w_wh1:
        loc_w2wwh1 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'WH1', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_w2wwh1)
    #7 VT xuất hàng kho Schenker
    loc_out_db = {'VN18'}
    for loc in loc_out_db:
        loc_outdb = LocationMethodFloor(loc, 'SCANOUT', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_outdb)
    #8 Vị trí hàng hủy
    lst_loc_hh = {'STEAM1', 'STEAM2'}
    for loc in lst_loc_hh:
        loc_hh = LocationMethodFloor(loc, 'REJECT', 'FL', 'FL', 'REJ', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_hh)
    #9 Vị trí Rework
    lst_loc_rw = {'FGLS', 'FGDM', 'DMGE', 'MATDM', 'LOST'}
    for loc in lst_loc_rw:
        loc_rw = LocationMethodFloor(loc, 'REWORK', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_rw)
    #10 Vị Trí cắt mẫu
    lst_loc_sam = {'SAMP', 'MCSAMP'}
    for loc in lst_loc_sam:
        loc_sam = LocationMethodFloor(loc, 'SAM', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_sam)
    #11 VT trả hàng lẻ
    lst_loc_return = {'STJP',}
    for loc in lst_loc_return:
        loc_rt = LocationMethodFloor(loc, 'RETURN', 'FL', 'FL', 'WH2', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_rt)
    #12 VT sàn kho Nhãn
    lst_loc_label_floor = {'LABEL1', 'LABEL2', 'LABEL3', 'LABEL4', 'LABEL5', 'LABEL6', 'LABEL7', 'LBSTEAM', 
                           'LABEL8A', 'LABEL8B', 'LABEL8C', 'LABEL8D', 'LABEL9A', 'LABEL9B', 'LABEL9C', 'LABEL9D'}
    for loc in lst_loc_label_floor:
        loc_lb_fl = LocationMethodFloor(loc, 'WW', 'FL', 'WW', 'LB', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_lb_fl)
    #13 VT tồn kho ngoài
    lst_loc_exwh = {'SGL2',}
    for loc in lst_loc_exwh:
        loc_exwh = LocationMethodFloor(loc, 'EXWH', 'FL', 'FL', 'EXWH', loc, level, 1, 1, 1).createlocfloor()
        loc_fl.append(loc_exwh)

    return loc_fl

def create_loc_pf_cool():
    DL = 'DUONG_LUONG'
    loc_pf = []
    loc_cool = []
    level = 0
    #PF1
    pf1_1 = ['Z1' + str(i).zfill(2) + j for i in range(4, 13) for j in ['A', 'B']]
    for loc in pf1_1:
        loc_pf1_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF1', 'PF1', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf1_1)

    pf1_2 = ['FZ1' + str(i).zfill(2) for i in range(8, 13)]
    for loc in pf1_2:
        loc_pf1_2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'PF1', 'PF1', level, 1, 1, 1, DL).createlocfloor()
        loc_pf.append(loc_pf1_2)
    #PF2
    pf2_1 = ['Z2' + str(i).zfill(2) + j for i in range(1, 5) for j in ['A', 'B']] +\
    ['Z2' + str(i).zfill(2) + j for i in range(13, 17) for j in ['A', 'B']]
    for loc in pf2_1:
        loc_pf2_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF2', 'PF2', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf2_1)

    pf2_2 = ['Z2' + str(i).zfill(2) for i in range(5, 13)]
    for loc in pf2_2:
        loc_pf2_2 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF2', 'PF2', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf2_2)

    pf2_3 = ['FZ2' + str(i).zfill(2) for i in [3, 4, 7, 8, 11, 12, 15, 16]]
    for loc in pf2_3:
        loc_pf2_3 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'PF2', 'PF2', level, 1, 1, 1, DL).createlocfloor()
        loc_pf.append(loc_pf2_3)

    #PF3
    pf3_1 = ['Z3' + str(i).zfill(2) + j for i in range(5, 13) for j in ['A', 'B']]    
    for loc in pf3_1:
        loc_pf3_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF3', 'PF3', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf3_1)

    pf3_2 = ['Z3' + str(i).zfill(2) for i in range(1, 17) if 1 <= i <= 4 or 13 <= i <= 16]
    for loc in pf3_2:
        loc_pf3_2 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF3', 'PF3', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf3_2)

    pf3_3 = ['FZ3' + str(i).zfill(2) for i in [3, 4, 7, 8, 11, 12, 15, 16]]
    for loc in pf3_3:
        loc_pf3_3 = LocationMethodFloor(loc, 'WW', 'FL', 'WW', 'PF3', 'PF3', level, 1, 1, 1, DL).createlocfloor()
        loc_pf.append(loc_pf3_3)
    
    #PF4
    pf4_1 = ['Z4' + str(i).zfill(2) + j for i in range(1, 17) for j in ['A', 'B', 'C'] if 1 <= i <= 8 or 13 <= i <= 16] +\
    ['Z4' + str(i).zfill(2) + j for i in range(9, 13) for j in ['A', 'B']]
    for loc in pf4_1:
        loc_pf4_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF4', 'PF4', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf4_1)

    pf4_2 = ['FZ4' + str(i).zfill(2) for i in [3, 4, 7, 8, 11, 12, 15, 16]]
    for loc in pf4_2:
        loc_pf4_2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'PF4', 'PF4', level, 1, 1, 1, DL).createlocfloor()
        loc_pf.append(loc_pf4_2)

    #PF5
    pf5_1 = ['Z5' + str(i).zfill(2) + j for i in range(1, 19) for j in ['A1', 'A2', 'B1', 'B2']]
    for loc in pf5_1:
        loc_pf5_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF5', 'PF5', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf5_1)

    pf5_2 = ['Z5' + str(i).zfill(2) for i in range(20, 69)] + ['Z5' + str(i).zfill(2) + 'A' for i in range(20, 52)]
    for loc in pf5_2:
        loc_pf5_2 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'PF5', 'PF5', level, 1, 1, 1).createlocfloor()
        loc_pf.append(loc_pf5_2)

    pf5_3 = ['FZ5' + str(i).zfill(2) for i in [4, 5, 6, 10, 11, 12, 16, 17, 18, 55, 56, 59, 60, 61, 65, 66, 67, 68]]
    for loc in pf5_3:
        loc_pf5_3 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'PF5', 'PF5', level, 1, 1, 1, DL).createlocfloor()
        loc_pf.append(loc_pf5_3)

    #COOLING1
    cl1 = ['PM' + str(i).zfill(2) + j for i in range(17, 20) for j in ['A', 'B']] +\
    ['PM' + str(i).zfill(2) + j for i in range(23, 31) for j in ['A', 'B']]
    for loc in cl1:
        loc_cl1_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'COOL1', 'COOL1', level, 1, 1, 1).createlocfloor()
        loc_cool.append(loc_cl1_1)
    #Đường luồng CL1 và 1 vị trí PM17C
    for loc in ('FPM18', 'FPM19'):
        loc_cl1_2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'COOL1', 'COOL1', level, 1, 1, 1, DL).createlocfloor()
        loc_cool.append(loc_cl1_2)
    #PM17C
    for loc in ('PM17C',):
        loc_cl1_3 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'COOL1', 'COOL1', level, 1, 1, 1).createlocfloor()
        loc_cool.append(loc_cl1_3)
    #COOLING2
    cl2= []
    for i in range(1, 32):
        if i == 1 or i == 31:
            cl2.append('PC' + str(i) + 'A')
        elif 2 <= i <= 30:
            if i == 18:
                for j in ['A', 'B', 'C', 'D']:
                    cl2.append('PC' + str(i) + j)
            else:
                for j in ['A', 'B']:
                    cl2.append('PC' + str(i) + j)

    for loc in cl2:
        loc_cl2_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'COOL2', 'COOL2', level, 1, 1, 1).createlocfloor()
        loc_cool.append(loc_cl2_1)

    for loc in {'COOL1', 'COOL2', 'COOL3'}:
        loc_cl2_2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'COOL2', 'COOL2', level, 1, 1, 1, DL).createlocfloor()
        loc_cool.append(loc_cl2_2)

    #COOLING3
    cl3 = ['EZ' + str(i).zfill(2) for i in range(1, 16)] + \
    ['EZ' + str(i).zfill(2) + j for i in range(15, 24) for j in ['A', 'B']]
    #mới chuyển vị trí EZ12 thành 3 vị trí A, B, C tháng 11/2024
    cl3.remove('EZ12')
    cl3 = cl3 + ['EZ12A', 'EZ12B', 'EZ12C']
    for loc in cl3:
        loc_cl3_1 = LocationMethodFloor(loc, 'MK', 'FL', 'FL', 'COOL3', 'COOL3', level, 1, 1, 1).createlocfloor()
        loc_cool.append(loc_cl3_1)

    cl3_1 = ['FEZ' + str(i).zfill(2) for i in [15, 17, 18, 19, 20, 21, 22, 23]]
    for loc in cl3_1:
        loc_cl3_2 = LocationMethodFloor(loc, 'WW', 'FL', 'FL', 'COOL3', 'COOL3', level, 1, 1, 1, DL).createlocfloor()
        loc_cool.append(loc_cl3_2)

    return loc_pf + loc_cool

# if __name__ == '__main__':
def main_createloc():
    loc_3wh = []
    lst_df = []
    wh1 = create_loc_wh1()
    wh2 = create_loc_wh2()
    wh3 = create_loc_wh3()
    lb = create_loc_label()
    fl = create_loc_floor()
    pf_cl = create_loc_pf_cool()
    loc_3wh = wh1 + wh2 + wh3 + lb + fl + pf_cl
    lst_columns = ['location', 'type_rack', 'cat_rack', 'type_loc', 'name_wh', 'name_rack',
                   'level', 'num_pallet', 'stack_limit', 'foot_print', 'note']
    for _, st in enumerate(loc_3wh):
        lst_df.append(st.split(';'))
    lst_zip = list(zip(*lst_df))
    lst_dict = dict(zip(lst_columns, lst_zip))
   
    df = pd.DataFrame(lst_dict).drop_duplicates()
    LocationNew().insert_data_from_df(df, 'replace')
    

