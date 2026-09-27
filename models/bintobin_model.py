import logging
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

from models.inventory_model import InventoryModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BintobinModel:
    def __init__(self, inveotory: InventoryModel):
        self.inventory_model = inveotory

    def real_file_import_inv_csv(self, link_file_inv_csv) -> pd.DataFrame:
        self.df_inv_csv = self.inventory_model._read_file_inv_prime(link_file_inv_csv)
        return self.df_inv_csv

    def read_file_demand(self, link_file_demand) -> pd.DataFrame:
        selected_sheets  = pd.read_excel(link_file_demand, sheet_name=["DEMAND EXPORT", "CTMZ,PDS,ST"])
        lst_demand = []
        for key in selected_sheets.keys():
            df_export = selected_sheets[key] #CTMZ,PDS,ST
            df = self._get_demand_sheet_by_sheet(df_export)
            lst_demand.append(df)
        self.df_demand = pd.concat(lst_demand, ignore_index=True)
        return self.df_demand

    def get_master_location(self) -> pd.DataFrame:
        self.location = self.inventory_model.get_location()

    def process_bintobin(self, df_tonkho: pd.DataFrame, df_demand: pd.DataFrame) ->pd.DataFrame:
        #Dùng vòng lặp
        #Lấy master_location
        self.get_master_location()
        #Lấy df tồn kho
        df_ton_kho = df_tonkho[df_tonkho['cat_inv']=='FG']

        # 2. TÍNH TỔNG LƯỢNG DƯ THỪA CẦN MOVE THEO MÃ (GCAS)
        # TÍNH TỔNG TỒN TẠI TẦNG 1 THEO ITEM
        # Xác định các vị trí thuộc tầng 1
        #is_tang_a = df_ton_kho['location'].str.contains('a$', na=False, case=False, regex=True).copy()
        df_location = self.location[["location", "location_system_type", "name_warehouse"]]
        df_tonkho = pd.merge(df_ton_kho, df_location, on='location', how='left')
        #Lọc tồn kho chỉ lấy tầng A của WH2
        mask_is_tang_a = pd.Series(True, df_tonkho.index)
        mask_is_tang_a &= df_tonkho['location_system_type'].isin(["PF"])
        mask_is_tang_a &= df_tonkho['name_warehouse'].isin(["WH2"])
        df_ton_tang_a = df_tonkho[mask_is_tang_a]

        # Nhóm tổng tồn tầng 1 của từng item
        df_tong_t1 = df_ton_tang_a.groupby('gcas')['qty'].sum().reset_index(name='tong_ton_tang_a')

        # df_tong_ton = df_ton_kho.groupby('gcas')['qty'].sum().reset_index(name='tong_ton')
        df_tong_demand = df_demand.groupby('gcas')['sl_demand'].sum().reset_index(name='sl_demand')
        df_tong_demand = df_tong_demand[df_tong_demand['sl_demand']>0]
        df_du_thua = pd.merge(df_tong_t1, df_tong_demand, left_on='gcas', right_on='gcas', how='left')


        # Nếu không có demand, SL_Demand = 0 -> Tổng dư thừa = Toàn bộ lượng tồn
        # df_du_thua['sl_demand'] = df_du_thua['sl_demand'].fillna(0)
        df_du_thua['sl_demand'] = pd.to_numeric(df_du_thua['sl_demand'], errors='coerce').fillna(0)
        df_du_thua['over_demand'] = np.maximum(df_du_thua['tong_ton_tang_a'] - df_du_thua['sl_demand'], 0)

        

        # 3. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)

        # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
        df_process = pd.merge(df_ton_tang_a, df_du_thua[['gcas', 'over_demand', 'tong_ton_tang_a', 'sl_demand']], on='gcas', how='left')
        #df_process = df_process[df_process['location'].str.contains('a$', na=False, case=False, regex=True)].copy()

        # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
        # Việc này giúp ưu tiên giải phóng các ô có số lượng ít trước (tối ưu không gian Bin)
        df_process = df_process.sort_values(by=['gcas', 'qty'], ascending=[True, True]).reset_index(drop=True)

        # Chuyển dữ liệu sang dạng mảng NumPy/List để vòng lặp chạy với tốc độ phần cứng (nhanh gấp hàng trăm lần lặp df)
        gcas_arr = df_process['gcas'].values
        ton_arr = df_process['qty'].values
        # du_thua_arr = df_process['over_demand'].values

        # TẠO DICTIONARY THEO DÕI: Key là mã GCAS, Value là lượng over_demand còn lại
        # Dictionary này đảm bảo mỗi mã GCAS chỉ có một "ví tiền" duy nhất để trừ dần
        demand_dict = dict(zip(df_du_thua['gcas'], df_du_thua['over_demand']))

        thung_can_move_list = []
        con_lai_can_lay_list = []

        for i in range(len(df_process)):
            current_gcas = gcas_arr[i]
            ton_tai_bin = ton_arr[i]
            
            # Lấy lượng nhu cầu còn lại của mã GCAS hiện tại từ Dictionary
            # Nếu mã này không nằm trong danh sách dư thừa, mặc định nhu cầu bằng 0
            #rem_needed là viết tắt của Remaining Needed (nghĩa là: Số lượng còn lại cần phải lấy thêm).
            rem_needed = demand_dict.get(current_gcas, 0)
            
            if rem_needed <= 0:
                move = 0
            elif ton_tai_bin > rem_needed:
                # Ô quá lớn -> Bỏ qua ô này, giữ nguyên nhu cầu
                move = 0
            else:
                # Ô nhỏ hơn hoặc bằng nhu cầu -> Lấy hết sạch ô này
                move = ton_tai_bin
                rem_needed -= move
                
                # CẬP NHẬT LẠI VÀO DICTIONARY: Lưu lại số lượng mới sau khi đã trừ
                demand_dict[current_gcas] = rem_needed
                
            thung_can_move_list.append(move)
            con_lai_can_lay_list.append(rem_needed)

        # Gán kết quả tính toán ngược lại vào DataFrame
        df_process['qty_need_move'] = thung_can_move_list
        df_process['available'] = con_lai_can_lay_list


        # 4. LỌC KẾT QUẢ CUỐI CÙNG
        final_move_list = df_process[df_process['qty_need_move'] > 0].copy()

        final_move_list = final_move_list[[
            'gcas', 'location', 'qty', 'tong_ton_tang_a', 'sl_demand', 'over_demand', 'qty_need_move', 'available'
        ]]

        # move_on  = 220
        # top = move_on
        # bot = top + 20
        # display(final_move_list.iloc[top:bot,])
        # print(df_du_thua[df_du_thua['gcas']==80755744])
        # print("--- DANH SÁCH VỊ TRÍ CẦN MOVE (LOGIC LÀM TRÒN XUỐNG DÙNG VÒNG LẶP) ---")
        # print(final_move_list[final_move_list['gcas']==80755744])
        return final_move_list

    def _get_demand_sheet_by_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        #Phiên bản fix cảnh báo lỗi pandas
        # 🛠️ Đoạn code hoàn chỉnh sau khi sửa lỗi để xử lý Data lớn:

        # 1. Đọc toàn bộ file Excel
        #1. Đọc file
        # df = selected_sheets["DEMAND EXPORT"]

        # 2. Tìm vị trí cột chứa chữ 'SKU' (Lấy phần tử đầu tiên của tuple)
        sku_mask = df.astype(str).apply(lambda x: x.str.strip().str.upper()) == 'SKU'
        sku_col_idx = np.where(sku_mask.any(axis=0))[0][0]

        # 3. Tìm vị trí cột chứa chữ 'CON LAI/CÒN LẠI'
        con_lai_mask = df.astype(str).apply(lambda x: x.str.strip().str.upper().str.contains('CON LAI|CÒN LẠI', regex=True))
        con_lai_col_idx = np.where(con_lai_mask.any(axis=0))[0][0]

        # Tọa độ cột Market = Cột SKU dịch sang phải 2 ô (Hết lỗi TypeError)
        market_col_idx = sku_col_idx + 2

        # 4. Trích xuất tên Market (Đã sửa lỗi FutureWarning bằng .astype(bool))
        is_next_row_sku = sku_mask.iloc[:, sku_col_idx].shift(-1).astype(bool).fillna(False)
        df['Market'] = np.where(is_next_row_sku, df.iloc[:, market_col_idx], np.nan)

        # Dùng ffill() để điền tên Market xuống các dòng dưới
        df['Market'] = df['Market'].ffill()

        # 5. Gộp dữ liệu thành bảng kết quả mới bằng cách chỉ định chỉ số cột cụ thể
        result_df = pd.DataFrame({
            'Market': df['Market'],
            'SKU': df.iloc[:, sku_col_idx],
            'sl_demand': df.iloc[:, con_lai_col_idx]
        })

        # 6. Lọc sạch dữ liệu: Chỉ giữ dòng có SKU là chữ số
        result_df['SKU_clean'] = result_df['SKU'].astype(str).str.strip()
        final_df = result_df[result_df['SKU_clean'].str.isdigit() == True].copy()

        # Giữ lại đúng 3 cột cần thiết theo yêu cầu
        final_df = final_df[['SKU', 'sl_demand', 'Market']]
        final_df = final_df.rename(columns={
            'SKU': 'gcas'
        })

        # Hiển thị kết quả kiểm tra
        return final_df


    