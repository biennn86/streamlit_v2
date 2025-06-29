# SELECT date FROM inventory ORDER BY rowid DESC LIMIT 1;
import pandas as pd
from read_tonkho.read_rpm import *
from controllers.masterdata import MasterData
from controllers.location_new import LocationNew
from controllers.tonkho import Inventory


class CreateDfToDB():
    def __init__(self, data_uploaded):
        self.data_uploaded = data_uploaded
        #Tạo một df merge giữa tồn kho, master data, master location
        self.dfTonkho = create_data_rtcis(self.data_uploaded)
        self.dfmasterData = MasterData().get_df_from_db()
        self.dfmasterData = self.dfmasterData[['gcas','description', 'cat', 'type1', 'type2', 'source', 'jit']]
        self.masterLocation = LocationNew().get_df_from_db()
        #đưa tồn kho vừa phân tích vào database
        import_tonkho_to_db(self.dfTonkho)
    
    def MergeTonkhoMtdataMtLoc(self):
        self.dfTonkho['gcas'] = pd.to_numeric(self.dfTonkho['gcas'], downcast='integer')
        self.dfTonkho['pallet'] = pd.to_numeric(self.dfTonkho['pallet'], downcast='integer')
        self.dfTonkho['qty'] = pd.to_numeric(self.dfTonkho['qty'], downcast='float')
        self.dfTonkho['batch'] = self.dfTonkho['batch'].astype(str)
        self.dfTonkho['vnl'] = self.dfTonkho['vnl'].astype(str)
        #chuyển kiểu dữ liệu cột gcas trong masterdata về int. Kiểu mặc định đang là obj
        self.dfmasterData['gcas'] = pd.to_numeric(self.dfmasterData['gcas'], downcast='integer')
        #khi update master data dùng method append để lấy được lịch sử thay đổi thông tin của gas (ví dụ như pallet pattern)
        #nên khi lấy master data ra phân tích phải loại bỏ trùng để tránh duplicate data đi merge.
        #khi dropduplicate giữ lại dòng cuối cùng để lấy thông tin data mới nhất
        self.dfmasterData = self.dfmasterData.drop_duplicates(subset=['gcas'], keep='last')
        
        # merge data của tồn kho, location, master data
        self.dfTonkhoMtData = pd.merge(left=self.dfTonkho, right=self.dfmasterData, on='gcas', how='left' )
        self.dfTonkhoMtDataMtLoc = pd.merge(self.dfTonkhoMtData, self.masterLocation, left_on='location', right_on='location', how='left') #suffixes=('_inv', '_loc')
        self.dfTonkhoMtDataMtLoc['num_pallet'] = pd.to_numeric(self.dfTonkhoMtDataMtLoc['num_pallet'], downcast='integer')
        self.dfTonkhoMtDataMtLoc['gcas'] = self.dfTonkhoMtDataMtLoc['gcas'].astype(str)
        self.dfTonghop = self.dfTonkhoMtDataMtLoc

        # self.dfTonkhoMtDataMtLoc.to_excel('data_tonghop.xlsx', index=False)
        # print(self.dfTonkhoMtDataMtLoc)

        return self.dfTonghop
    
    def EmptyLoc(self):
        self.dfMergeLocInv = pd.merge(self.masterLocation, self.dfTonkho, on='location', how='left', indicator=True)
        # Lọc ra các hàng chỉ có trong df1
        self.dfMergeLocInv = self.dfMergeLocInv[(self.dfMergeLocInv['_merge'] == 'left_only') &  
                                       ((self.dfMergeLocInv['type_rack'] == 'HR') |
                                        (self.dfMergeLocInv['type_rack'] == 'PF') |
                                        (self.dfMergeLocInv['type_rack'] == 'MK'))]
        self.dfMergeLocInv = self.dfMergeLocInv.drop('_merge', axis=1)
         #Chuyển astype cột pallet sang number
        self.dfMergeLocInv['num_pallet'] = pd.to_numeric(self.dfMergeLocInv['num_pallet'], downcast='integer')
        self.dfMergeLocInv = self.dfMergeLocInv[['location', 'type_rack', 'name_wh', 'num_pallet']].reset_index(drop=True)
        #Thêm cột Note
        self.dfMergeLocInv.insert(4, 'note', 'Empty')
        # # Chia nhỏ df
        # index = np.array_split(self.dfMergeLocInv.index, 25)
        # self.dfs = [self.dfMergeLocInv.loc[idx] for idx in index]
        # # Đặt lại chỉ số cho từng DataFrame
        # for df in self.dfs:
        #     df.reset_index(drop=False, inplace=True)
        # # Hợp nhất các DataFrame nhỏ theo chiều ngang
        # self.dfEmptyLoc = pd.concat(self.dfs, axis=1, ignore_index=False)
        # self.dfEmptyLoc.rename(columns={'index': 'STT', 'location': 'Location', 'type_rack': 'Type', 'name_wh': 'Name_Wh', 'num_pallet': 'Num_Pallet', 'note': 'Note'}, inplace=True)
        # self.dfEmptyLoc.to_excel('EmptyLoc.xlsx', index=False)
        # # print(self.dfEmptyLoc)
        # return self.dfEmptyLoc
        #=================
        # self.dfMergeLocInv = self.dfMergeLocInv.sort_values(by=['name_wh'], ascending=True).reset_index(drop=False)
        self.dfMergeLocInv.index = range(1, len(self.dfMergeLocInv)+1)
        self.dfMergeLocInv = self.dfMergeLocInv.reset_index(drop=False)
        self.dfMergeLocInv['type_rack'] = self.dfMergeLocInv['type_rack'].map({
            'PF': 'Level A',
            'HR': 'Hight Rack',
            'MK': 'Marking'
        })
        self.dfMergeLocInv.rename(columns={
            'index': 'STT',
            'location': 'Location',
            'type_rack': 'Type Rack',
            'name_wh': 'WH Name',
            'num_pallet': 'Number Pallet',
            'note': 'Status'
        }, inplace=True)

        self.df_emptyloc = self.dfMergeLocInv
        # self.df_emptyloc.to_excel('EmptyLoc.xlsx', index=False)
        return self.df_emptyloc
    
    def FindMixup(self):
        #Tìm data trùng lặp trên cột 'location'
        self.duplicates = self.dfTonkho.duplicated(subset=['location'], keep=False)
        #Lọc và sort data trùng lặp đưa vào một df mới
        self.df_duplicates = self.dfTonkho[self.duplicates].sort_values(by=['location'])
        #Điều kiện lấy mixup. Gcas và bactch trên cùng một location phải khác nhau
        self.df_getmixup_gcas_batch = self.df_duplicates[(self.df_duplicates['gcas'] != self.df_duplicates['gcas'].shift()) |
                                        (self.df_duplicates['batch'] != self.df_duplicates['batch'].shift())]
        #Lọc lại df một lần nữa để loại bỏ tiếp dòng có gcas và batch giống nhau nhưng vẫn cùng vị trí. Ví dụ như rack double deep
        #Những vị trí trùng có cùng gcas, lot thì dòng code trên sẽ giữ lại dòng last
        self.df_mixup_eo_fg_rpm = self.df_getmixup_gcas_batch[self.df_getmixup_gcas_batch.duplicated(subset=['location'], keep=False)].reset_index(drop=True)
        #Lọc ra df co cat_inv là EO và remove những dòng có location duplicates
        self.df_eo = self.df_mixup_eo_fg_rpm[self.df_mixup_eo_fg_rpm['cat_inv'] == 'EO']
        self.df_unipue_eo =  self.df_eo.drop_duplicates(subset=['location'], keep=False)
        #Lọc df có cat_inv là FG và RPM
        self.df_mixup_fg_rpm = self.df_mixup_eo_fg_rpm[(self.df_mixup_eo_fg_rpm['cat_inv'] == 'FG') |
                                                       (self.df_mixup_eo_fg_rpm['cat_inv'] == 'RPM')]
        #Nối 2 df EO và (FG, RPM) lại. 
        self.df_mixup_lost_row_eo_duplicates = pd.concat([self.df_mixup_fg_rpm, self.df_unipue_eo], axis=0, ignore_index=True).sort_values(by=['location'])
        #Xử lý tiếp vấn đề df EO có những dòng cùng gcas và có mixup với FG & RPM
        #Lấy những dòng có location không trùng nhau. Trong python '~' là phủ định
        self.unique_fg_rpm = ~self.df_mixup_lost_row_eo_duplicates.duplicated(['location'], keep=False)
        #Tạo series những dòng có location không trùng nhau, nghĩa là đang ở single
        self.df_unique = self.df_mixup_lost_row_eo_duplicates[self.unique_fg_rpm].location
        #lấy lại data EO đã bị drop_duplicates ở trên
        self.df_eo_deleted = self.df_eo[self.df_eo['location'].isin(self.df_unique)]
        self.df_mixup_allloc = pd.concat([self.df_mixup_lost_row_eo_duplicates, self.df_eo_deleted], axis=0, ignore_index=True).sort_values(by=['location'])
        #Lọc những vị trí cần lấy
        self.df_mixup_final = pd.merge(left=self.df_mixup_allloc, right=self.masterLocation, on=['location'], how='left')
        self.df_mixup_final =  self.df_mixup_final[self.df_mixup_final['type_rack'].isin(['HR', 'PF', 'MK']) & 
                                                   self.df_mixup_final['type_loc'].isin(['DB', 'ST', 'FL', 'SV', 'OB'])]
        self.df_mixup_final = self.df_mixup_final[['date', 'location', 'gcas', 'batch', 'vnl', 'status', 'qty', 'pallet']].reset_index(drop=True)
        self.df_mixup_final = self.df_mixup_final.astype(str)
        # print(self.df_mixup_final)
        # self.df_mixup_final.to_excel('Mixup.xlsx', index=False)
        #đổi tên cột
        self.df_mixup_final.rename(columns={
            'date': 'Date',
            'location': 'Location',
            'gcas': 'Gcas',
            'batch': 'Batch',
            'vnl': 'VNL',
            'status': 'Status',
            'qty': 'Qty',
            'pallet': 'Pallet'
        }, inplace=True)

        # print(self.df_mixup_final['location'].nunique())
        return self.df_mixup_final

    def CombineBin(self):
        #Merge df tồn kho và df masterlocation
        self.df_merge_inv_and_loc = pd.merge(left=self.dfTonkho, right=self.masterLocation, on=['location'], how='left')
        #Lọc rack cần combine
        self.df_rack_mutiple = self.df_merge_inv_and_loc[(self.df_merge_inv_and_loc['type_rack'].isin(['HR', 'PF'])) &
                                                         (self.df_merge_inv_and_loc['type_loc'].isin(['DB', 'ST', 'OB'])) &
                                                         (self.df_merge_inv_and_loc['cat_inv'].isin(['FG', 'RPM']))]
        self.df_rack_combine = self.df_rack_mutiple.copy()
        #cover to number pallet và num_pallet
        self.df_rack_combine['pallet'] = pd.to_numeric(self.df_rack_combine['pallet'], downcast='integer')
        self.df_rack_combine['num_pallet'] = pd.to_numeric(self.df_rack_combine['num_pallet'], downcast='integer')
        self.df_rack_combine['qty'] = pd.to_numeric(self.df_rack_combine['qty'], downcast='integer')
        self.df_rack_combine['gcas'] = self.df_rack_combine['gcas'].astype(str)
        self.df_rack_combine['batch'] = self.df_rack_combine['batch'].astype(str)
        self.df_rack_combine['vnl'] = self.df_rack_combine['vnl'].astype(str)
        #Lấy ra những bin trong tồn kho đang có 1 pallet
        self.df_singlepallet_allbin = self.df_rack_combine[(self.df_rack_combine['pallet'] == 1)]
        
        #--------------------
        #chèn thêm 1 cột To_Locaion vào trong dataframe
        # self.df_singlepallet_allbin['to_location'] = 'NaN'
        # for row in self.df_singlepallet_allbin.itertuples():
        #     index = row.Index
        #     gcas = [row.gcas]
        #     batch = [row.batch]
        #     loc = [row.location]
        #     check = ((self.df_singlepallet_allbin['gcas'].isin(gcas)) &
        #             (self.df_singlepallet_allbin['batch'].isin(batch)) &
        #             (self.df_singlepallet_allbin['num_pallet'] == 2))
            
        #     index_row = check.idxmax()
        #     if index_row > 0:
        #         to_loc = self.df_singlepallet_allbin.loc[check.idxmax()].location
        #         self.df_singlepallet_allbin.loc[index_row, 'to_location'] = to_loc
        # print(self.df_singlepallet_allbin)
        #     # self.df_singlepallet_allbin.iloc[index, 20] = self.df_singlepallet_allbin[check][0].location
        #     # self.df_singlepallet_allbin.iloc[index, 21] = self.df_singlepallet_allbin[check].location.iloc[0]
        #     # print(self.df_singlepallet_allbin.loc[check.idxmax()].location)
        # self.df_singlepallet_allbin.to_excel('CombineBin.xlsx', index=False)
            # if check.bool():
            #     print(row.location)
        #--------------------
        #Tạo series đã có trong df_singlepallet_allbin
        # loc_exists_single_pallet = self.df_singlepallet_allbin.location
        #Tạo df To_Location bỏ những bin đã có trong df_singlepallet_allbin
        # loc_is_in_df_single = self.df_merge_inv_and_loc['location'].isin(loc_exists_single_pallet)
        self.df_to_location = self.df_singlepallet_allbin[::-1]
        #lấy ra những bin trong hệ thống là doubledeep đang có trong tồn kho
        self.df_bin_doubledeep = self.df_to_location[(self.df_to_location['num_pallet'] == 2)]
        #Merge những dòng có cùng gcas, batch giữa 2 df
        self.df_merged = pd.merge(left=self.df_singlepallet_allbin, right=self.df_bin_doubledeep, on=['gcas', 'batch'], how='inner', suffixes=['_left', '_right'])
        #Loại bỏ form_loc, to_loc có cùng vị trí
        self.remove_duplicates_onrow = self.df_merged.query("location_left != location_right")
        #Loại bỏ vị trí trùng 2 cột to_loc và from_loc
        self.remove_duplicates_colleft = self.remove_duplicates_onrow.drop_duplicates(subset=['location_left'], keep='first')
        self.remove_duplicates_colright = self.remove_duplicates_colleft.drop_duplicates(subset=['location_right'], keep='first')
        #Xóa dòng có location trong côt to_loc đã xuất hiện trong côt from_loc
            #Lấy loc trong cột from_loc tìm trong cột to_loc bằng phương thức isin()
            #`Lấy index những dòng isin lọc ra được, dùng drop đưa index vào để xóa những dòng đó
        list_from_loc = self.remove_duplicates_colright.location_left
        index_delete =  self.remove_duplicates_colright[self.remove_duplicates_colright['location_right'].isin(list_from_loc)].index
        self.df_delete_bin_to_loc = self.remove_duplicates_colright.drop(index_delete)
        #Thu gọn lại nhũng cột cần lấy
        self.df_combinebin = self.df_delete_bin_to_loc[['date_left', 'gcas', 'batch', 'vnl_left', 'status_left', 'qty_left', 'pallet_left', 'location_left', 'location_right']]
        self.df_combinebin = self.df_combinebin.sort_values(by='location_left').reset_index(drop=True)
        self.df_combinebin.index = range(1, len(self.df_combinebin)+1)
        self.df_combinebin = self.df_combinebin.sort_values(by='location_left').reset_index(drop=False)
        self.df_combinebin.rename(columns={'index': 'STT',
                                           'date_left': 'DateTime',
                                           'gcas': 'Gcas',
                                           'batch': 'Batch',
                                           'vnl_left': 'VNL',
                                           'status_left': 'Status',
                                           'qty_left': 'Qty',
                                           'pallet_left': 'Pallet',
                                           'location_left': 'From Location',
                                           'location_right': 'To Loaction'}, inplace=True)
        # print(self.df_combinebin)
        # self.df_combinebin.to_excel('CombineBin.xlsx', index=False)
        return self.df_combinebin
    
    def Get_Inventory(self):
        self.df_inventory = Inventory().get_all_inv()
        self.df_inventory.index = range(1, len(self.df_inventory)+1)
        self.df_inventory = self.df_inventory.reset_index(drop=False)
        self.df_inventory.rename(columns={
            'index': 'STT',
            'date': 'DateTime',
            'gcas': 'Gcas',
            'batch': 'Batch',
            'vnl': 'VNL',
            'status': 'Status',
            'qty': 'Qty',
            'pallet': 'Pallet',
            'location': 'Location',
            'note_inv': 'Note',
            'cat_inv': 'Category'
        }, inplace=True)
        return self.df_inventory

class DashboarTonkho():
    #tạo 1 df tổng hợp số pallet theo kho và type location tương ứng
    def __init__(self, dfTonghop):
        self.dfTonghop = dfTonghop
        self.datetime = self.dfTonghop.iloc[0, 0]
        self.dfMtLoc = LocationNew().get_df_from_db()
        self.columns = self.dfTonghop.columns.to_list()
        self.dictCol = {}
        for i, col in enumerate(self.columns):
            self.dictCol[i] = col

    def GetTypeRack(self, nameWh) -> list:
        NAMEWH = nameWh
        typeRack = self.dfMtLoc[self.dfMtLoc['name_wh']== NAMEWH].groupby('type_rack').nunique().index.to_list()
        return typeRack
    def GetTypeLoc(self, nameWh) -> list:
        NAMEWH = nameWh
        typeLoc = self.dfMtLoc[self.dfMtLoc['name_wh']== NAMEWH].groupby('type_loc').nunique().index.to_list()
        return typeLoc
    def GetNameWH(self) -> list:
        nameWH = self.dfMtLoc.groupby('name_wh').nunique().index.to_list()
        return nameWH
    def GetTypeCat(self) -> list:
        typeCat = self.dfTonghop.groupby('cat_inv').nunique().index.to_list()
        return typeCat
    
    def CountPalletWhithWh(self, namewh, typerack, typeloc, cat, option) -> int:
        dict_query = {
            1: "name_wh == '{}' & type_rack == '{}' & type_loc == '{}' & cat_inv == '{}'".format(namewh, typerack, typeloc, cat),
        }
        
        soPallet = self.dfTonghop.query(dict_query[option]).agg({'pallet': 'sum'})[0]
        return soPallet
    
    def SumPalletWH(self):
        lst_nameWH = self.GetNameWH()
        lst_typeCat = self.GetTypeCat()
        dictPlWithTypeWh = {}
        #tạo dict theo type rack
        for NAMEWH in lst_nameWH:
            typeRackWithWh = self.GetTypeRack(NAMEWH)
            typeLocWithWh = self.GetTypeLoc(NAMEWH)
            for Tr in typeRackWithWh:
                for Tl in typeLocWithWh:
                    for cat in lst_typeCat:
                        fString = NAMEWH + '_' + Tr + '_' + Tl + '_' + cat
                        dictPlWithTypeWh[fString.lower()] = self.CountPalletWhithWh(NAMEWH, Tr, Tl, cat, 1)
        
        dfSumPlWithWhTypeCat = pd.DataFrame(tuple(dictPlWithTypeWh.items()), columns=['type', 'value'])
        dfSumPlWithWhTypeCat['wh'] = dfSumPlWithWhTypeCat['type'].apply(lambda x: x.split('_')[0])
        dfSumPlWithWhTypeCat['typerack'] = dfSumPlWithWhTypeCat['type'].apply(lambda x: x.split('_')[1])
        dfSumPlWithWhTypeCat['typeloc'] = dfSumPlWithWhTypeCat['type'].apply(lambda x: x.split('_')[2])
        dfSumPlWithWhTypeCat['cat'] = dfSumPlWithWhTypeCat['type'].apply(lambda x: x.split('_')[3])
        dfSumPlWithWhTypeCat.pop('type')
        dfSumPlWithWhTypeCat.insert(3, 'value', dfSumPlWithWhTypeCat.pop('value'))
        dfSumPlWithWhTypeCat = dfSumPlWithWhTypeCat.reindex(columns=['wh', 'typerack', 'typeloc', 'cat', 'value'])
        #Thêm datatile vào df Final
        dfSumPlWithWhTypeCat.insert(0, 'datetime', self.datetime)
        # df = df.groupby(['wh', 'typeloc', 'cat']).agg({'value': 'sum'}).reset_index()
        # dfSumPlWithWhTypeCat.to_excel('moi.xlsx', index=False)
        return dfSumPlWithWhTypeCat
      





































































































































































































        # dicWhInDictTypeCat = {}
        #từ dict trên tạo ra df tổng hợp số pallet theo kho và type location
        # for key in dictPlWithTypeWh.keys():
        #     dictLocTypeCat = {}
        #     lstKey = key.split('_')
        #     tLoc = lstKey[0]
        #     tDetailLoc = lstKey[1]
        #     nameWh = lstKey[2]
        #     tCat = lstKey[3]
        #     lstTypeDetailRack = self.GetTypeDetailWithNameRack(nameWh)
        #     if nameWh in ('COOL', 'PF'):
        #         lstNamerack = self.GetTypeWithNameRack(nameWh)
        #         lstTypeOrNameRack = lstNamerack
        #     else:
        #         lst_typeLoc = self.GetTypeRack(nameWh)
        #         lstTypeOrNameRack = lst_typeLoc

        #     for tLoc in lstTypeOrNameRack:
        #         for tCat in lst_typeCat:
        #             keyGetValue = tLoc + '_' + tDetailLoc + '_' + nameWh + '_' + tCat
        #             keyDictGetPalet = tLoc + '_' + tDetailLoc + '_' + tCat
        #             dictLocTypeCat[keyDictGetPalet.lower()] =  dictPlWithTypeWh.get(keyGetValue, 0)
        #     dicWhInDictTypeCat.update({nameWh.lower(): dictLocTypeCat.copy()})
        # df = pd.DataFrame.from_dict(dicWhInDictTypeCat, orient='index')
        # df.reset_index(inplace=True, names='wh')
        # #melt tạo df từ chiều ngang thành chiều dọc
        # df_melt = pd.melt(df, id_vars = 'wh', var_name='var', value_name='value')
        # df_melt = df_melt.dropna().reset_index(drop=True)
        # df_melt.to_excel('df_melt_kho.xlsx', index=False)
        # print(df_melt)









# class SummaryPalletWhithWh():
#     def __init__(self, dictData):
#         self.dictData = dictData
#         self.dictNameWh = self.__CreateObj()

#     def __CreateObj(self):
#         self.dictPalletWh = {}
#         self.__dictNameWh = {}
#         typeLoc = ['HR', 'IN', 'PF', 'PICK', 'REWORK', 'SCANOUT', 'MK']
#         typeCat = ['FG', 'RPM', 'EO']
#         for key in self.dictData.keys():
#             self.nameWh = key[key.find('_') + 1 : key.rfind('_')]
#             for tLoc in typeLoc:
#                 for tCat in typeCat:
#                     keyGetValue = tLoc + '_' + self.nameWh + '_' + tCat
#                     keyDictGetPalet = tLoc + '_' + tCat
#                     self.dictPalletWh[keyDictGetPalet.lower()] =  self.dictData.get(keyGetValue, 0)

#             # obj = CreateIntense(self.dictPalletWh)
#             self.__dictNameWh.update({self.nameWh.lower(): self.dictPalletWh.copy()})
          
#         df = pd.DataFrame.from_dict(self.__dictNameWh, orient='index')
#         df.reset_index(inplace=True, names='wh')
#         df_melt = pd.melt(df, id_vars = 'wh', var_name='var', value_name='value')
#         df_melt.to_excel('df_melt_kho.xlsx', index=False)
#         print(df)
#         print(df_melt)

#         # print(self.__dictNameWh)
#         # print(obj.hr_fg)
#         return self.__dictNameWh

# class CreateIntense():
#     def __init__(self, dictLoc):
#         self.__dict__.update(dictLoc)