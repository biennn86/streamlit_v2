class BaseCountPallet():
    '''
    Trả về số pallet được query từ dataframe tồn kho.
    Sử dụng 3 thuộc tính name wh, typerack và cat của hàng
    '''
    def __init__(self, df, namewh, typerack, cat):
        self.df = df
        self.namewh = namewh.upper()
        self.typerack = typerack.upper()
        self.cat = cat.upper()
        
    def CountDetailLoc(self):
        try:
            QUERY = "name_wh == '{}' & type_rack == '{}' & cat_inv == '{}'".format(self.namewh, self.typerack, self.cat)
            NumPalet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return NumPalet
        except Exception as err:
            return None
        
class CountPalletDAHO(BaseCountPallet):
    '''
    Kế thừa từ class BasecountPallet, add thêm thuộc tính type_loc.
    Trả về số pallet được query từ df tồn kho dùng riêng cho rack DA và HO
    '''
    def __init__(self, df, namewh, typerack, cat, typeloc):
        super().__init__(df, namewh, typerack, cat)
        self.typeloc = typeloc.upper()

    def CountDetailLoc_DAHO(self):
        try:
            QUERY = "name_wh == '{}' & type_rack == '{}' & type_loc == '{}' & cat_inv == '{}'".format(self.namewh, self.typerack, self.typeloc, self.cat)
            NumPalet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return NumPalet
        except Exception as err:
            return None
        
class CountPallet_FgRpmEo():
    '''
    Lấy total pallet FG, RPM bằng cách.
    Query cột cat_inv để lọc ra hàng EO, FG, RPM
    Query cột type1 để lọc ra đâu là raw_mat, pack_mat, finished_goods và cả blank
    Query cột name_wh để đếm pallet trong WH1, WH2, WH3
    '''
    def __init__(self, df,  cat_inv, type1=None):
        self.df = df
        self.cat_inv= cat_inv.upper()
        self.type1 = type1

    def CoutPallet_Fg(self):
        try:
            QUERY = "cat_inv == '{}' & (name_wh == 'WH1' | name_wh == 'WH2' | name_wh == 'WH3')".format(self.cat_inv)
            # mới: QUERY = "cat_inv == '{}'".format(self.cat_inv)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
    
    def CoutPallet_Pm(self):
        #Phải lấy luôn cả pack_mat và blank. Nên phương án đưa ra là loại bỏ hàng raw_mat là đáp ứng đc yc
        #name_wh.isnull() -> lấy luôn cả dòng name_wh trống
        try:
            QUERY = "cat_inv == '{}' & type1 != '{}' & (name_wh == 'WH1' | name_wh == 'WH2' | name_wh == 'WH3')".format(self.cat_inv, self.type1)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
    def CoutPallet_Rm(self):
        #Lấy type1 = raw_mat, không lấy blank vì blank đã lấy ở PM, nếu lấy sẽ bị double
        #Chỉ lấy RM ở WH1,2,3 không lấy ở khác kho đặc biệt
        try:
            QUERY = "cat_inv == '{}' & type1 == '{}' & (name_wh == 'WH1' | name_wh == 'WH2' | name_wh == 'WH3')".format(self.cat_inv, self.type1)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
    
    def CoutPallet_Eo(self):
        #lấy tổng trong file EO trừ vị trí kho REJ (steam#1, steam#2)
        try:
            QUERY = "cat_inv == '{}' & name_wh != 'REJ'".format(self.cat_inv)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
class CountPalletWithCat():
    def __init__(self, df,  cat_inv, cat_mtdata=None, type2=None):
        self.df = df
        self.cat_inv = cat_inv
        self.cat_mtdata = cat_mtdata
        self.type2 = type2

    def Fg_Cat(self):
        #Count Pallet theo Cat dwn, febz, hdl dựa vào cat_inv và cat (masterdata)
        try:
            QUERY = "cat_inv == '{}' & cat == '{}' & (name_wh == 'WH1' | name_wh == 'WH2' | name_wh == 'WH3')".format(self.cat_inv, self.cat_mtdata)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
    def Pm_Cat(self):
        #Cout pallet theo cat_inv và type2 shipper, pouch, bottle
        try:
            QUERY = "cat_inv == '{}' & type2 == '{}' & (name_wh == 'WH1' | name_wh == 'WH2' | name_wh == 'WH3')".format(self.cat_inv, self.type2)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None


class CountPalletWithLoc():
    def __init__(self, df, location):
        self.df = df
        self.location = location.upper()
    
    def CountPallet(self):
        try:
            QUERY = "location == '{}'".format(self.location)
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
class CountPalletBlock():
    def __init__(self, df, cat_inv = None):
        self.df = df
        self.cat_inv = cat_inv

    def CountTotalPlBlock(self):
        try:
            QUERY = "status == 'HD' & (name_wh != 'REJ' & name_wh != 'LSL')"
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
    def CountPlBlockFG(self):
        try:
            QUERY = "status == 'HD' & cat_inv == 'FG' & (name_wh != 'REJ' & name_wh != 'LSL')"
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None
        
    def CountPlBlockLB(self):
        try:
            QUERY = "status == 'HD' & cat_inv == 'RPM' & name_wh == 'LB'"
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None

class CountPalletJIT():
    def __init__(self, df):
        self.df = df 
    def PalletJIT(self):
        try:
            QUERY = "jit == 'JIT'"
            num_pallet = self.df.query(QUERY).agg({'pallet': 'sum'})[0]
            return num_pallet
        except Exception as err:
            return None