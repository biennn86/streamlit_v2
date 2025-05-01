import pandas as pd
from utils.constants import Columns
from controllers.location_new import LocationNew
from controllers.masterdata import MasterData

class MergeDataModel:
    def get_location(self):
        df_location = LocationNew().get_df_from_db()
        return df_location
    
    def get_masterdata(self):
        df_masterdata = MasterData().get_df_from_db()
        df_masterdata = df_masterdata[Columns.COLUMNS_MASTERDATA_NEED.value]
        return df_masterdata
    
    def merge_inv_loc_masterdata(self, df_inv):
        '''
        Khi update master data dùng method append để lấy được lịch sử thay đổi thông tin của gas (ví dụ như pallet pattern)
        nên khi lấy master data ra phân tích phải loại bỏ trùng để tránh duplicate data đi merge.
        Khi dropduplicate giữ lại dòng cuối cùng để lấy thông tin data mới nhất
        Trả về Dataframe tổng hợp giữa tồn kho, location, masterdata.
        '''
        if df_inv is None:
            exit()
            
        self.df_location = self.get_location()
        self.df_masterdata = self.get_masterdata()
        df_inv['gcas'] = pd.to_numeric(df_inv['gcas'], downcast='integer')
        df_inv['pallet'] = pd.to_numeric(df_inv['pallet'], downcast='integer')
        df_inv['qty'] = pd.to_numeric(df_inv['qty'], downcast='float')
        df_inv['batch'] = df_inv['batch'].astype(str)
        df_inv['vnl'] = df_inv['vnl'].astype(str)
        #chuyển kiểu dữ liệu cột gcas trong masterdata về int. Kiểu mặc định đang là obj
        self.df_masterdata['gcas'] = pd.to_numeric(self.df_masterdata['gcas'], downcast='integer')
        self.df_masterdata = self.df_masterdata.drop_duplicates(subset=['gcas'], keep='last')
        
        # merge data của tồn kho, location, master data
        self.dfTonkhoMtData = pd.merge(df_inv, self.df_masterdata, left_on='gcas', right_on='gcas', how='left' )
        self.dfTonkhoMtDataMtLoc = pd.merge(self.dfTonkhoMtData, self.df_location, left_on='location', right_on='location', how='left') #suffixes=('_inv', '_loc')
        self.dfTonkhoMtDataMtLoc['num_pallet'] = pd.to_numeric(self.dfTonkhoMtDataMtLoc['num_pallet'], downcast='float')
        self.dfTonkhoMtDataMtLoc['gcas'] = self.dfTonkhoMtDataMtLoc['gcas'].astype(str)
        self.dfTonghop = self.dfTonkhoMtDataMtLoc
        # self.dfTonkhoMtDataMtLoc.to_excel('data_tonghop.xlsx', index=False)
        return self.dfTonghop