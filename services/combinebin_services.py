import pandas as pd
import typing as Dict

class CombineBin:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy(deep=True)
        self._cover_tonumeric_df()

    def _cover_tonumeric_df(self) -> None:
        self.df['pallet'] = pd.to_numeric(self.df['pallet'], downcast='integer')
        self.df['pallet_capacity'] = pd.to_numeric(self.df['pallet_capacity'], downcast='integer')


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
        #Lọc df1 với các tiêu chí như dưới. df1 là df đi dò tìm
        mask = pd.Series(True, self.df.index)
        mask &= self.df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
        mask &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask &= self.df['location_system_type'].isin(['hr', 'pf', 'ww'])
        mask &= (self.df['location_usage_type'] != 'sv')
        mask &= self.df['pallet'] == 1
        df1 = self.df[mask].copy()
        df1.insert(len(df1.columns.to_list()), 'to_location', None)

        #Lọc df1 với các tiêu chí như dưới. df1 bị dò tìm
        mask_1 = pd.Series(True, self.df.index)
        mask_1 &= self.df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
        mask_1 &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask_1 &= (self.df['level'] != '0')&(self.df['level'] != 'a')
        mask_1 &= self.df['pallet'] == 1
        mask_1 &= self.df['pallet_capacity'] == 2

        df2 = self.df[mask_1]
        df2 = df2[['gcas', 'batch', 'status', 'location']].copy().sort_values(by='location')
        df2.insert(len(df2.columns.to_list()), 'note_geted', 0)

        #Loại bỏ nhưng loc có trong df2 ra khỏi df1
        #Tránh lấy trùng vị trí
        location_in_df2 = df2['location'].to_list()
        is_in_df1 = df1['location'].isin(location_in_df2)
        df1_filtered = df1[~is_in_df1].sort_values(by='location').reset_index(drop=True)


        for i in range(len(df1_filtered)):
            gcas_from = df1_filtered.loc[i, 'gcas']
            batch_from = df1_filtered.loc[i, 'batch']
            status_from = df1_filtered.loc[i, 'status']
          
            #So sánh cột 'note_geted' để tăng xác xuất lấy được nhiều vị trí hơn
            #Vì hàm any() sẽ dừng lại ở dòng true đầu tiên, và có thể dòng đó 'note_geted' lại bằng 1
            #vì vòng lặp chạy trừ trên xuống
            gcas_comparison = (df2['note_geted'].isin([0]))&\
                (df2['gcas'].isin([gcas_from]))
                    
            batch_comparison = (df2['note_geted'].isin([0]))&\
                (df2['batch'].isin([batch_from]))
            
            status_comparison = (df2['note_geted'].isin([0]))&\
                (df2['status'].isin([status_from]))
            

            if all([gcas_comparison.any(), batch_comparison.any(), status_comparison.any()]):
                id_to_loc = gcas_comparison.idxmax()
               
                if df2.loc[id_to_loc, 'note_geted'] == 0:
                    to_loc = df2.loc[id_to_loc, 'location']
                    #cập nhập cột 'note_geted' = 1 để thể hiện vị trí đó đã lấy
                    df2.loc[id_to_loc, 'note_geted'] = 1
                    #cập nhập to_location và df from_location với index là i
                    df1_filtered.loc[i, 'to_location'] = to_loc
        
        ##lấy cột to_location khác None
        mask_2 = df1_filtered['to_location'].isnull()
        df1_filtered = df1_filtered[~mask_2].sort_values(by='location').reset_index(drop=True)

        return df1_filtered