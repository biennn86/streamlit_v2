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
        ''' df của RTCIS thì cột pallet là tổng pallet trong location đấy, nhưng tồn kho của Prime thì cột pallet luôn có giá trị là 1,
            vì hệ thống Prime quản lý theo LPN
            Combine bin sẽ lấy số lượng cột pallet để biết được số lượng pallet trong location đó là bao nhiêu pallet để xác đinh to_location
            có để thêm được 1 pallet trong location của rack double deep hay không
            Nên để chạy 1 lúc import được cả 2 dạng tồn kho RTCIS và Prime
            phải biết được tồn nào là của RTCIS và tồn nào của PRime
            Cách nhận biết:
            Kiểm tra cột pallet nếu giá trị là 1 hết thì đó là tồn kho Prime, ngược lại là tồn kho RTCIS
            Nếu tồn hiện tại là của RTCIS thì giữ nguyên giá trị cột pallet
            Nếu tồn hiện tại là của Prime tính lại cột pallet sẽ count theo số lượng location của cột location
        '''
        #Check df là của RTCIS hay Prime
        if (self.df['pallet']==1).all():
            self.df['pallet'] = self.df.groupby('location')['location'].transform('count')
            
        #Lọc df1 với các tiêu chí như dưới. df1 là df đi dò tìm (from_location)
        mask_from_location = pd.Series(True, self.df.index)
        mask_from_location &= self.df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
        mask_from_location &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask_from_location &= self.df['location_system_type'].isin(['hr', 'pf', 'ww'])
        mask_from_location &= (self.df['location_usage_type'] != 'sv')
        mask_from_location &= self.df['pallet'] == 1
        df_from_location = self.df[mask_from_location].copy()
        df_from_location.insert(len(df_from_location.columns.to_list()), 'to_location', None)

        #Lọc df2 với các tiêu chí như dưới. df2 bị dò tìm (to_location)
        mask_to_location = pd.Series(True, self.df.index)
        mask_to_location &= self.df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
        mask_to_location &= self.df['cat_inv'].isin(['fg', 'rpm'])
        mask_to_location &= (self.df['level'] != '0')&(self.df['level'] != 'a')
        mask_to_location &= self.df['pallet'] == 1
        mask_to_location &= self.df['pallet_capacity'] == 2

        df_to_location = self.df[mask_to_location]
        df_to_location = df_to_location[['gcas', 'batch', 'status', 'location']].copy().sort_values(by='location')
        df_to_location.insert(len(df_to_location.columns.to_list()), 'note_geted', 0)

        #Loại bỏ nhưng location có trong df_to_location ra khỏi df_from_location. Tránh lấy trùng vị trí
        location_in_df_to_location = df_to_location['location'].to_list()
        location_in_df_from_location = df_from_location['location'].isin(location_in_df_to_location)
        #df_from_location sau khi đã bỏ những location trong df_to_location. Dùng để chạy vòng lặp và tìm to_location
        df_from_location_only = df_from_location[~location_in_df_from_location].sort_values(by='location').reset_index(drop=True)

        #ĐI TÌM VỊ TRÍ TO_LOCATION KHỚP VỚI DF_FROM_LOCATION
        # 1. Định nghĩa các cột dùng làm khóa khớp dữ liệu
        keys = ['gcas', 'batch', 'status']

        # 2. Đánh số thứ tự xuất hiện (seq) độc lập cho từng nhóm ở cả 2 bảng
        df_from_location_only['seq'] = df_from_location_only.groupby(keys).cumcount()
        df_to_location['seq'] = df_to_location.groupby(keys).cumcount()

        # 3. Sử dụng merge để khớp cặp 1-đối-1 dựa trên khóa và số thứ tự
        merged = df_from_location_only.merge(
            df_to_location[keys + ['seq', 'location']], 
            on=keys + ['seq'], 
            how='left', 
            suffixes=('', '_from_location')
        )

        # 4. Gán vị trí tìm được sang cột 'to_location'
        merged['to_location'] = merged['location_from_location']

        # 5. Lọc bỏ dòng trống (không tìm thấy vị trí phù hợp), sắp xếp và dọn dẹp
        final_df = merged[merged['to_location'].notnull()].copy()
        final_df = final_df.drop(columns=['seq']).sort_values(by='location').reset_index(drop=True)

        return final_df
    
'''
cách 1: vẫn để cột note_geted
# 1. Lọc trước df2 lấy những dòng chưa được lấy (note_geted == 0)
df2_available = df2[df2['note_geted'] == 0].copy()

# 2. Tạo số thứ tự xuất hiện cho từng nhóm định danh ở cả 2 dataframe
# Việc này giúp khớp dòng 1 của df1 với dòng 1 của df2, dòng 2 của df1 với dòng 2 của df2...
group_cols = ['gcas', 'batch', 'status']
df1_filtered['occurrence'] = df1_filtered.groupby(group_cols).cumcount()
df2_available['occurrence'] = df2_available.groupby(group_cols).cumcount()

# 3. Sử dụng Merge để khớp dữ liệu dựa trên tổ hợp 4 cột (thay thế hoàn toàn vòng lặp)
df_merged = df1_filtered.merge(
    df2_available[group_cols + ['occurrence', 'location']], 
    on=group_cols + ['occurrence'], 
    how='left', 
    suffixes=('', '_df2')
)

# 4. Cập nhật kết quả vào cột 'to_location'
df_merged['to_location'] = df_merged['location_df2']

# 5. Cập nhật lại trạng thái 'note_geted' = 1 cho các dòng đã được khớp trong df2 gốc
# Tìm các index của df2 đã được sử dụng thành công trong df_merged
matched_df2_indices = df2_available.merge(
    df_merged[group_cols + ['occurrence']], 
    on=group_cols + ['occurrence'], 
    how='inner'
).index

df2.loc[matched_df2_indices, 'note_geted'] = 1

# 6. Loại bỏ cột phụ, lọc bỏ dòng trống, sắp xếp và trả về kết quả
result_df = df_merged[df_merged['to_location'].notnull()].copy()
result_df = result_df.drop(columns=['occurrence']).sort_values(by='location').reset_index(drop=True)

return result_df
============================================================================================================
#cách 2: bỏ cột note_geted
# 1. Định nghĩa các cột dùng làm khóa khớp dữ liệu
keys = ['gcas', 'batch', 'status']

# 2. Đánh số thứ tự xuất hiện (seq) độc lập cho từng nhóm ở cả 2 bảng
df1_filtered['seq'] = df1_filtered.groupby(keys).cumcount()
df2['seq'] = df2.groupby(keys).cumcount()

# 3. Sử dụng merge để khớp cặp 1-đối-1 dựa trên khóa và số thứ tự
merged = df1_filtered.merge(
    df2[keys + ['seq', 'location']], 
    on=keys + ['seq'], 
    how='left', 
    suffixes=('', '_from_df2')
)

# 4. Gán vị trí tìm được sang cột 'to_location'
merged['to_location'] = merged['location_from_df2']

# 5. Lọc bỏ dòng trống (không tìm thấy vị trí phù hợp), sắp xếp và dọn dẹp
final_df = merged[merged['to_location'].notnull()].copy()
final_df = final_df.drop(columns=['seq']).sort_values(by='location').reset_index(drop=True)

return final_df
==========================================================================
CÁCH NGUYÊN THỦY. DÙNG VÒNG LẶP FOR
        # for i in range(len(df_from_location_only)):
        #     gcas_from = df_from_location_only.loc[i, 'gcas']
        #     batch_from = df_from_location_only.loc[i, 'batch']
        #     status_from = df_from_location_only.loc[i, 'status']
          
        #     #So sánh cột 'note_geted' để tăng xác xuất lấy được nhiều vị trí hơn
        #     #Vì hàm any() sẽ dừng lại ở dòng true đầu tiên, và có thể dòng đó 'note_geted' lại bằng 1
        #     #vì vòng lặp chạy trừ trên xuống
        #     # Gộp chung cả 3 điều kiện và note_geted == 0 vào cùng một bộ lọc
        #     combined_comparison = (df_to_location['note_geted'] == 0) & \
        #                   (df_to_location['gcas'] == gcas_from) & \
        #                   (df_to_location['batch'] == batch_from) & \
        #                   (df_to_location['status'] == status_from)
            

        #     if combined_comparison.any():
        #         id_to_loc = combined_comparison.idxmax()
               
        #         if df_to_location.loc[id_to_loc, 'note_geted'] == 0:
        #             to_loc = df_to_location.loc[id_to_loc, 'location']
        #             #cập nhập cột 'note_geted' = 1 để thể hiện vị trí đó đã lấy
        #             df_to_location.loc[id_to_loc, 'note_geted'] = 1
        #             #cập nhập to_location và df from_location với index là i
        #             df_from_location_only.loc[i, 'to_location'] = to_loc
        
        # ##lấy cột to_location khác None
        # mask_2 = df_from_location_only['to_location'].isnull()
        # df_final = df_from_location_only[~mask_2].sort_values(by='location').reset_index(drop=True)

        # return df_final
'''
'''
Giải thích cách sử dụng groupby và cumcount() kết hợp với merge để tìm vị trí combine bin:

Không bao giờ xảy ra tình trạng lấy sót vị trí to_location
Lý do là vì hàm groupby() kết hợp với merge không xét cột seq một cách độc lập, mà nó bắt buộc phải khớp ĐỒNG THỜI cả 4 cột.
Hãy xem ví dụ trực quan dưới đây để hiểu tại sao không có chuyện "giành chỗ":
1. Cách seq sinh ra trong từng nhóm riêng biệt
Hàm .groupby(['gcas', 'batch', 'status']).cumcount() sẽ đếm số thứ tự riêng cho từng nhóm, chứ không đếm chung cho toàn bộ bảng.
Giả sử dữ liệu của bạn có 2 nhóm hàng khác nhau: sữa Milo và bánh Oreo. Pandas sẽ đánh số seq độc lập như sau:
Trong df1_filtered:
Dòng 1: Milo -> Nhóm Milo xuất hiện lần 1 -> seq = 0
Dòng 2: Oreo -> Nhóm Oreo xuất hiện lần 1 -> seq = 0 (Số 0 này hoàn toàn khác số 0 của Milo)
Dòng 3: Milo -> Nhóm Milo xuất hiện lần 2 -> seq = 1
Trong df2_avail (Vị trí kho):
Dòng 1: Vị trí A (Milo) -> seq = 0
Dòng 2: Vị trí B (Oreo) -> seq = 0
Dòng 3: Vị trí C (Milo) -> seq = 1
2. Khi merge, Pandas tìm chính xác cả 4 điều kiện
Câu lệnh merge của chúng ta quy định điều kiện khớp là:on=['gcas', 'batch', 'status', 'seq']
Khi Dòng 2 của df1 (Oreo, seq=0) đi tìm vị trí, Pandas sẽ kiểm tra toàn bộ bảng df2:
Xem Dòng 1 của df2 (Milo, seq=0): Thấy trùng seq=0 nhưng sai tên hàng (Oreo != Milo) -> Bỏ qua, không lấy.
Xem Dòng 2 của df2 (Oreo, seq=0): Thấy trùng cả tên hàng Oreo lẫn seq=0 -> Khớp lệnh thành công! Dòng này lấy được Vị trí B.
Tương tự, Dòng 3 của df1 (Milo, seq=1) sẽ bỏ qua dòng Oreo và khớp chính xác với Dòng 3 của df2 (Milo, seq=1) để lấy Vị trí C.
KẾT LUẬN
Số seq=0 của nhóm này không liên quan và không thể chiếm chỗ của số seq=0 của nhóm khác. Chúng ở các "vũ trụ" nhóm khác nhau.
Phép toán merge hoạt động giống như việc bạn đi tìm chìa khóa cho ổ khóa: phải trùng cả Nhãn hiệu (gcas, batch, status) và Mã răng cưa (seq) thì mới mở được. Do đó, code đảm bảo khớp chính xác 100% và không bị sót vị trí.
'''