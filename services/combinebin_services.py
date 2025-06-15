import pandas as pd
import typing as Dict

class CombineBin:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy(deep=True)
        self._cover_tonumeric_df()

    def _cover_tonumeric_df(self) -> None:
        self.df['pallet'] = pd.to_numeric(self.df['pallet'], downcast='integer')
        self.df['num_pallet'] = pd.to_numeric(self.df['num_pallet'], downcast='integer')


    def get_combinebin(self) -> pd.DataFrame:
        """ Tạo df1 lấy những vị trí đang có tồn 1 pallet trong df nguồn
            Tạo df2 lấy những vị trí có tồn 1 pallet đang ở bin có type_loc là db
            Lặp qua df1 lấy gcas, lot tìm trong df2 nếu có thì thêm vào cột mới có tên To_Location
            Loại bỏ những loc có trong df2 khỏi df1 để tránh bị trùng vị trí
            df_single_pl_rackdb['gcas'] == gcas_from: kết quả là môt series bool
            Để trả về kết quả duy nhất là true/false thì dùng hàm any().
            Trả về True nếu ít nhất một phần tử trong Series boolean là True.
            Trả về False nếu tất cả các phần tử đều là False.
            ------------
            Lấy Index của dòng True đầu tiên sau khi kiểm tra bằng any()
            Bằng cách sử dụng hàm idxmax()
            idxmax() sẽ trả về index của giá trị True (vì True được coi là 1 và False là 0, nên True là giá trị lớn nhất).
        """
        mask = pd.Series(True, self.df.index)
        mask &= self.df['name_wh'].isin(['wh1', 'wh2', 'wh3'])
        mask &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask &= self.df['type_rack'].isin(['hr', 'pf', 'ww'])
        mask &= (self.df['type_loc'] != 'sv')
        mask &= self.df['pallet'] == 1
        df_single_pl = self.df[mask].copy()
        df_single_pl.insert(len(df_single_pl.columns.to_list()), 'to_location', None)

        mask_1 = pd.Series(True, self.df.index)
        mask_1 &= self.df['name_wh'].isin(['wh1', 'wh2', 'wh3'])
        mask_1 &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask_1 &= (self.df['level'] != '0')&(self.df['level'] != 'a')
        mask_1 &= self.df['pallet'] == 1
        mask_1 &= self.df['num_pallet'] == 2

        df_single_pl_rackdb = self.df[mask_1].copy()
        df_single_pl_rackdb = df_single_pl_rackdb[['gcas', 'batch', 'status', 'location']]
        df_single_pl_rackdb.insert(len(df_single_pl_rackdb.columns.to_list()), 'note_get', 0)

        #Loại bỏ nhưng loc có trong df_single_pl_rackdb ra khỏi df_single_pl
        #Tránh lấy trùng vị trí
        location_in_df2 = df_single_pl_rackdb['location'].to_list()
        is_in_df2 = df_single_pl['location'].isin(location_in_df2)
        df1_filtered = df_single_pl[~is_in_df2].reset_index(drop=True)

        for i in range(len(df1_filtered)):
            gcas_from = df1_filtered.loc[i, 'gcas']
            batch_from = df1_filtered.loc[i, 'batch']
            status_from = df1_filtered.loc[i, 'status']
          
            #So sánh cột 'note_get' để tăng xác xuất lấy được nhiều vị trí hơn
            #Vì hàm any() sẽ dừng lại ở dòng true đầu tiên, và có thể dòng đó 'note_get' lại bằng 1
            #vì vòng lặp chạy trừ trên xuống
            gcas_comparison = (df_single_pl_rackdb['note_get'].isin([0]))&\
                (df_single_pl_rackdb['gcas'].isin([gcas_from]))
                    
            batch_comparison = (df_single_pl_rackdb['note_get'].isin([0]))&\
                (df_single_pl_rackdb['batch'].isin([batch_from]))
            
            status_comparison = (df_single_pl_rackdb['note_get'].isin([0]))&\
                (df_single_pl_rackdb['status'].isin([status_from]))
            

            if all([gcas_comparison.any(), batch_comparison.any(), status_comparison.any()]):
                id_to_loc = gcas_comparison.idxmax()
               
                if df_single_pl_rackdb.loc[id_to_loc, 'note_get'] == 0:
                    to_loc = df_single_pl_rackdb.loc[id_to_loc, 'location']
                    #cập nhập cột 'note_get' = 1 để thể hiện vị trí đó đã lấy
                    df_single_pl_rackdb.loc[id_to_loc, 'note_get'] = 1
                    #cập nhập to_location và df from_location với index là i
                    df1_filtered.loc[i, 'to_location'] = to_loc
        
        ##lọc cột to_location khác None
        mask_2 = df1_filtered['to_location'].isnull()
        df1_filtered = df1_filtered[~mask_2].sort_values(by='location').reset_index(drop=True)

        return df1_filtered