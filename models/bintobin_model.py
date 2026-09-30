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

    def read_file_demand(self, link_file_demand) -> Dict[str, pd.DataFrame]:
        selected_sheets  = pd.read_excel(link_file_demand, sheet_name=["DEMAND EXPORT", "CTMZ,PDS,ST"])
        dict_demand = {}
        for key in selected_sheets.keys():
            df_export = selected_sheets[key] #CTMZ,PDS,ST
            df = self._get_demand_sheet_by_sheet(df_export)

            if key in ["DEMAND EXPORT"]:
                key_dict = "demand_export"
            elif key in ["CTMZ,PDS,ST"]:
                key_dict = "demand_pds"

            dict_demand[key_dict] = df
        #self.df_demand = pd.concat(lst_demand, ignore_index=True)
        return dict_demand

    def get_master_location(self) -> pd.DataFrame:
        location = self.inventory_model.get_location()
        return location

    def process_bintobin_standard(self, df_inventory: pd.DataFrame, dict_demand: Dict[str, pd.DataFrame]) ->pd.DataFrame:
        #Version mới nhất
        # Chiến thuật này tính chừa PDS trên tổng tồn kho theo từng item
        #Lấy demand export và demand pds
        df_demand_export = dict_demand.get("demand_export", pd.DataFrame()).rename(columns={"sl_demand": "qty_export"})
        df_demand_pds = dict_demand.get("demand_pds", pd.DataFrame()).rename(columns={"sl_demand": "qty_pds"})
        df_demand_export = df_demand_export[df_demand_export["qty_export"]>0].groupby("gcas", as_index=False)["qty_export"].sum()
        df_demand_pds = df_demand_pds[df_demand_pds["qty_pds"]>0].groupby("gcas", as_index=False)["qty_pds"].sum()
        #Lấy master_location
        location = self.get_master_location()
        #Lấy df tồn kho FG
        df_inventory = df_inventory[df_inventory['cat_inv']=='FG']

        # Bước 1: Tính toán tồn kho chi tiết (Tầng 1 riêng và Các tầng cao riêng)
        df_location = location[["location", "location_system_type", "name_warehouse"]]
        df_inventory = pd.merge(df_inventory, df_location, on='location', how='left')
        #Lọc tồn kho chỉ lấy tầng A của WH2
        mask_is_t1 = pd.Series(True, df_inventory.index)
        mask_is_t1 &= df_inventory['location_system_type'].isin(["PF", "WW"])
        mask_is_t1 &= df_inventory['name_warehouse'].isin(["WH2"])
        df_inv_t1 = df_inventory[mask_is_t1]
        #Lọc tồn tầng cao để tính chừa pds
        mask_is_hr = pd.Series(True, df_inventory.index)
        mask_is_hr &= df_inventory['location_system_type'].isin(["HR"])
        df_inv_high = df_inventory[mask_is_hr]
        # Nhóm tổng tồn tầng a của từng item
        df_inv_grp_t1 = df_inv_t1.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_t1'})
        # Nhóm tổng tồn tầng cao của từng item
        df_inv_grp_high = df_inv_high.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_high'})
        # Bước 2: Gộp tất cả dữ liệu (Tồn kho + Demand) vào một bảng tổng master theo SKU
        # Dùng thuât toán outer merge để không sót bất kỳ SKU nào xuất hiện ở các file
        df_master = pd.merge(df_inv_grp_t1, df_inv_grp_high, on='gcas', how='outer')
        df_master = pd.merge(df_master, df_demand_pds, on='gcas', how='left')
        df_master = pd.merge(df_master, df_demand_export, on='gcas', how='left')
        # Điền giá trị 0 cho các ô trống (NaN)
        df_master = df_master.fillna(0).infer_objects(copy=False)
        # Bước 3: Tính toán theo Logic tổng kho
        # 3.1. Tính Tổng tồn kho toàn hệ thống
        df_master['total_inv'] = df_master['inv_t1'] + df_master['inv_high']
        # 3.2. Tính toán xem Tổng kho đã đáp ứng đủ PDS chưa, nếu thừa thì còn lại bao nhiêu khả dụng
        df_master['inv_after_pds'] = np.maximum(0, df_master['total_inv'] - df_master['qty_pds'])
        # 3.3. Xác định lượng hàng được phép GIỮ LẠI ở Tầng 1 để xuất Export trong ngày
        # Nó phải thỏa mãn: Không vượt quá tồn Tầng 1, không vượt quá lượng khả dụng sau PDS, và không vượt quá nhu cầu Export
        df_master['keep_t1'] = np.minimum(
            df_master['inv_t1'], 
            np.minimum(df_master['inv_after_pds'], df_master['qty_export'])
        )
        # 3.4. Tính Lượng hàng cần bốc từ Tầng 1 lên Tầng cao
        df_master['qty_to_move'] = df_master['inv_t1'] - df_master['keep_t1']
        # Bước 4: Xuất kết quả danh sách lệnh chuyển hàng
        #inv_t1, inv_high, qty_pds,	qty_export,	total_inv, inv_after_pds, keep_t1, qty_to_move
        df_move_action = df_master[df_master['qty_to_move'] > 0]#[['gcas', 'inv_t1', 'keep_t1', 'qty_to_move']]
        # Bước 4. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)
        # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
        df_process = pd.merge(df_inv_t1, df_move_action, on='gcas', how='left')
        # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
        # Việc này giúp ưu tiên giải phóng các ô có số lượng ít trước (tối ưu không gian Bin)
        df_process = df_process.sort_values(by=['gcas', 'qty'], ascending=[True, True]).reset_index(drop=True)

        # Chuyển dữ liệu sang dạng mảng NumPy/List để vòng lặp chạy với tốc độ phần cứng (nhanh gấp hàng trăm lần lặp df)
        gcas_arr = df_process['gcas'].values
        ton_arr = df_process['qty'].values
        # du_thua_arr = df_process['over_demand'].values

        # TẠO DICTIONARY THEO DÕI: Key là mã GCAS, Value là lượng over_demand còn lại
        # Dictionary này đảm bảo mỗi mã GCAS chỉ có một "ví tiền" duy nhất để trừ dần
        demand_dict = dict(zip(df_move_action['gcas'], df_move_action['qty_to_move']))

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

        # final_move_list = final_move_list[[
        #     'gcas', 'location', 'qty', 'inv_t1', 'inv_high', 'total_inv', 'qty_pds', 'qty_export', 'inv_after_pds', 'keep_t1', 'qty_to_move', 'qty_need_move', 'available', 'location_system_type'
        # ]]

        return final_move_list

    def process_bintobin_greedy(self, df_inventory: pd.DataFrame, dict_demand: Dict[str, pd.DataFrame]) ->pd.DataFrame:
        #Version mới nhất
        # Chiến thuật này tính chừa PDS trên tồn kho tầng cao. Ưu tiên chừa PDS là tối thường và 100% hàng PDS phải đưa lên tầng cao
        #Lấy demand export và demand pds
        df_demand_export = dict_demand.get("demand_export", pd.DataFrame()).rename(columns={"sl_demand": "qty_export"})
        df_demand_pds = dict_demand.get("demand_pds", pd.DataFrame()).rename(columns={"sl_demand": "qty_pds"})
        df_demand_export = df_demand_export[df_demand_export["qty_export"]>0].groupby("gcas", as_index=False)["qty_export"].sum()
        df_demand_pds = df_demand_pds[df_demand_pds["qty_pds"]>0].groupby("gcas", as_index=False)["qty_pds"].sum()
        #Lấy master_location
        location = self.get_master_location()
        #Lấy df tồn kho FG
        df_inventory = df_inventory[df_inventory['cat_inv']=='FG']

        # Bước 1: Tính toán tồn kho chi tiết (Tầng 1 riêng và Các tầng cao riêng)
        df_location = location[["location", "location_system_type", "name_warehouse"]]
        df_inventory = pd.merge(df_inventory, df_location, on='location', how='left')
        #Lọc tồn kho chỉ lấy tầng A của WH2
        mask_is_t1 = pd.Series(True, df_inventory.index)
        mask_is_t1 &= df_inventory['location_system_type'].isin(["PF", "WW"])
        mask_is_t1 &= df_inventory['name_warehouse'].isin(["WH2"])
        df_inv_t1 = df_inventory[mask_is_t1]
        #Lọc tồn tầng cao để tính chừa pds
        mask_is_hr = pd.Series(True, df_inventory.index)
        mask_is_hr &= df_inventory['location_system_type'].isin(["HR"])
        df_inv_high = df_inventory[mask_is_hr]
        # Nhóm tổng tồn tầng a của từng item
        df_inv_grp_t1 = df_inv_t1.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_t1'})
        # Nhóm tổng tồn tầng cao của từng item
        df_inv_grp_high = df_inv_high.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_high'})
        # Bước 2: Gộp tất cả dữ liệu (Tồn kho + Demand) vào một bảng tổng master theo SKU
        # Dùng thuât toán outer merge để không sót bất kỳ SKU nào xuất hiện ở các file
        df_master = pd.merge(df_inv_grp_t1, df_inv_grp_high, on='gcas', how='outer')
        df_master = pd.merge(df_master, df_demand_pds, on='gcas', how='left')
        df_master = pd.merge(df_master, df_demand_export, on='gcas', how='left')
        # Điền giá trị 0 cho các ô trống (NaN)
        df_master = df_master.fillna(0).infer_objects(copy=False)
        # Bước 2: Tính lượng PDS còn THIẾU trên tầng cao cần phải bù vào
        df_master['pds_needed_high'] = np.maximum(0, df_master['qty_pds'] - df_master['inv_high'])
        # Bước 3: Tính lượng tồn Tầng 1 còn lại sau khi đã ưu tiên cấu đi để bù vào PDS trên tầng cao
        df_master['t1_available_after_pds'] = np.maximum(0, df_master['inv_t1'] - df_master['pds_needed_high'])
        # Bước 4: Lượng thực tế GIỮ LẠI ở Tầng 1 để xuất hàng trong ngày (Export)
        df_master['keep_t1'] = np.minimum(df_master['t1_available_after_pds'], df_master['qty_export'])
        # Bước 5: Lượng hàng bốc từ Tầng 1 lên tầng cao (Bao gồm PDS thiếu + Tồn thừa export)
        df_master['qty_to_move'] = df_master['inv_t1'] - df_master['keep_t1']
        df_move_action = df_master[df_master['qty_to_move'] > 0]#[['gcas', 'inv_t1', 'keep_t1', 'qty_to_move']]
        # Bước 6. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)
        # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
        df_process = pd.merge(df_inv_t1, df_move_action, on='gcas', how='left')
        # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
        # Việc này giúp ưu tiên giải phóng các ô có số lượng ít trước (tối ưu không gian Bin)
        df_process = df_process.sort_values(by=['gcas', 'qty'], ascending=[True, True]).reset_index(drop=True)

        # Chuyển dữ liệu sang dạng mảng NumPy/List để vòng lặp chạy với tốc độ phần cứng (nhanh gấp hàng trăm lần lặp df)
        gcas_arr = df_process['gcas'].values
        ton_arr = df_process['qty'].values
        # du_thua_arr = df_process['over_demand'].values

        # TẠO DICTIONARY THEO DÕI: Key là mã GCAS, Value là lượng over_demand còn lại
        # Dictionary này đảm bảo mỗi mã GCAS chỉ có một "ví tiền" duy nhất để trừ dần
        demand_dict = dict(zip(df_move_action['gcas'], df_move_action['qty_to_move']))

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

        # final_move_list = final_move_list[[
        #     'gcas', 'location', 'qty', 'inv_t1', 'inv_high', 'total_inv', 'qty_pds', 'qty_export', 'inv_after_pds', 'keep_t1', 'qty_to_move', 'qty_need_move', 'available', 'location_system_type'
        # ]]

        return final_move_list

    def _get_demand_sheet_by_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
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
            'SKU': 'gcas',
            'Market': 'market'
        })

        # Hiển thị kết quả kiểm tra
        return final_df

#==========================================================================================================================
# def process_bintobin(self, df_tonkho: pd.DataFrame, dict_demand: Dict[str, pd.DataFrame]) ->pd.DataFrame:
#         #Dùng vòng lặp. Version đầu tiên
#         #Lấy demand export và demand pds
#         df_demand_export = dict_demand.get("demand_export", pd.DataFrame())
#         df_demand_pds = dict_demand.get("demand_pds", pd.DataFrame())
#         #Lấy master_location
#         self.get_master_location()
#         #Lấy df tồn kho
#         df_ton_kho = df_tonkho[df_tonkho['cat_inv']=='FG']

#         # 2. TÍNH TỔNG LƯỢNG DƯ THỪA CẦN MOVE THEO MÃ (GCAS)
#         # TÍNH TỔNG TỒN TẠI TẦNG 1 THEO ITEM
#         # Xác định các vị trí thuộc tầng 1
#         #is_tang_a = df_ton_kho['location'].str.contains('a$', na=False, case=False, regex=True).copy()
#         df_location = self.location[["location", "location_system_type", "name_warehouse"]]
#         df_tonkho = pd.merge(df_ton_kho, df_location, on='location', how='left')
#         #Lọc tồn kho chỉ lấy tầng A của WH2
#         mask_is_tang_a = pd.Series(True, df_tonkho.index)
#         mask_is_tang_a &= df_tonkho['location_system_type'].isin(["PF", "WW"])
#         mask_is_tang_a &= df_tonkho['name_warehouse'].isin(["WH2"])
#         df_ton_tang_a = df_tonkho[mask_is_tang_a]
#         #Lọc tồn tầng cao để tính chừa pds
#         mask_is_hr = pd.Series(True, df_tonkho.index)
#         mask_is_hr &= df_tonkho['location_system_type'].isin(["HR"])
#         df_ton_hr = df_tonkho[mask_is_hr]
        
#         # Nhóm tổng tồn tầng a của từng item
#         df_tong_ton_tang_a = df_ton_tang_a.groupby('gcas')['qty'].sum().reset_index(name='tong_ton_tang_a')
#         # Nhóm tổng tồn tầng cao của từng item
#         df_tong_ton_tang_cao = df_ton_hr.groupby('gcas')['qty'].sum().reset_index(name='tong_ton_tang_cao')

#         #Tìm và tính toán item không có trong demand và item có tồn vượt demand
#         # df_tong_ton = df_ton_kho.groupby('gcas')['qty'].sum().reset_index(name='tong_ton')
#         df_tong_demand_export = df_demand_export.groupby('gcas')['sl_demand'].sum().reset_index(name='sl_demand')
#         df_tong_demand_export = df_tong_demand_export[df_tong_demand_export['sl_demand']>0]
#         df_du_thua_export = pd.merge(df_tong_ton_tang_a, df_tong_demand_export, left_on='gcas', right_on='gcas', how='left')
#         # Nếu không có demand, SL_Demand = 0 -> Tổng dư thừa = Toàn bộ lượng tồn
#         # df_du_thua['sl_demand'] = df_du_thua['sl_demand'].fillna(0)
#         df_du_thua_export['sl_demand'] = pd.to_numeric(df_du_thua_export['sl_demand'], errors='coerce').fillna(0)
#         df_du_thua_export['over_demand'] = np.maximum(df_du_thua_export['tong_ton_tang_a'] - df_du_thua_export['sl_demand'], 0)

#         #Tìm và tính toán item có trong demand_pds
#         df_tong_demand_pds = df_demand_pds.groupby('gcas')['sl_demand'].sum().reset_index(name='sl_demand')
#         df_tong_demand_pds = df_tong_demand_pds[df_tong_demand_pds['sl_demand']>0]
#         df_du_thua_pds = pd.merge(df_tong_ton_tang_cao, df_tong_demand_pds, left_on='gcas', right_on='gcas', how='left')
#         df_du_thua_pds['sl_demand'] = pd.to_numeric(df_du_thua_pds['sl_demand'], errors='coerce').fillna(0)
#         df_du_thua_pds['over_demand'] = np.maximum(df_du_thua_pds['sl_demand'] - df_du_thua_pds['tong_ton_tang_cao'], 0)
#         df_du_thua_pds = df_du_thua_pds[df_du_thua_pds['over_demand']>0]
        
        
        
#         # Đưa df_demand_pds và cột overdemand của df_du_thua
#         df_du_thua = pd.concat(
#             [
#                 df_du_thua_export,
#                 pd.DataFrame(
#                     {
#                         "gcas": df_du_thua_pds["gcas"],
#                         "sl_demand": df_du_thua_pds["sl_demand"],
#                         "over_demand": df_du_thua_pds["over_demand"],
#                         "tong_ton_tang_a": df_du_thua_pds["tong_ton_tang_cao"],
#                     }
#                 ),
#             ],
#             ignore_index=True,
#         )
#         # df_du_thua = pd.concat([df_du_thua_export, df_du_thua_pds], ignore_index=True)
        

#         # 3. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)
#         # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
#         df_process = pd.merge(df_ton_tang_a, df_du_thua[['gcas', 'over_demand', 'tong_ton_tang_a', 'sl_demand']], on='gcas', how='left')
#         #df_process = df_process[df_process['location'].str.contains('a$', na=False, case=False, regex=True)].copy()
       

#         # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
#         # Việc này giúp ưu tiên giải phóng các ô có số lượng ít trước (tối ưu không gian Bin)
#         df_process = df_process.sort_values(by=['gcas', 'qty'], ascending=[True, True]).reset_index(drop=True)

#         # Chuyển dữ liệu sang dạng mảng NumPy/List để vòng lặp chạy với tốc độ phần cứng (nhanh gấp hàng trăm lần lặp df)
#         gcas_arr = df_process['gcas'].values
#         ton_arr = df_process['qty'].values
#         # du_thua_arr = df_process['over_demand'].values

#         # TẠO DICTIONARY THEO DÕI: Key là mã GCAS, Value là lượng over_demand còn lại
#         # Dictionary này đảm bảo mỗi mã GCAS chỉ có một "ví tiền" duy nhất để trừ dần
#         demand_dict = dict(zip(df_du_thua['gcas'], df_du_thua['over_demand']))

#         thung_can_move_list = []
#         con_lai_can_lay_list = []

#         for i in range(len(df_process)):
#             current_gcas = gcas_arr[i]
#             ton_tai_bin = ton_arr[i]
            
#             # Lấy lượng nhu cầu còn lại của mã GCAS hiện tại từ Dictionary
#             # Nếu mã này không nằm trong danh sách dư thừa, mặc định nhu cầu bằng 0
#             #rem_needed là viết tắt của Remaining Needed (nghĩa là: Số lượng còn lại cần phải lấy thêm).
#             rem_needed = demand_dict.get(current_gcas, 0)
            
#             if rem_needed <= 0:
#                 move = 0
#             elif ton_tai_bin > rem_needed:
#                 # Ô quá lớn -> Bỏ qua ô này, giữ nguyên nhu cầu
#                 move = 0
#             else:
#                 # Ô nhỏ hơn hoặc bằng nhu cầu -> Lấy hết sạch ô này
#                 move = ton_tai_bin
#                 rem_needed -= move
                
#                 # CẬP NHẬT LẠI VÀO DICTIONARY: Lưu lại số lượng mới sau khi đã trừ
#                 demand_dict[current_gcas] = rem_needed
                
#             thung_can_move_list.append(move)
#             con_lai_can_lay_list.append(rem_needed)

#         # Gán kết quả tính toán ngược lại vào DataFrame
#         df_process['qty_need_move'] = thung_can_move_list
#         df_process['available'] = con_lai_can_lay_list


#         # 4. LỌC KẾT QUẢ CUỐI CÙNG
#         final_move_list = df_process[df_process['qty_need_move'] > 0].copy()

#         final_move_list = final_move_list[[
#             'gcas', 'location', 'qty', 'tong_ton_tang_a', 'sl_demand', 'over_demand', 'qty_need_move', 'available', 'location_system_type'
#         ]]

#         # move_on  = 220
#         # top = move_on
#         # bot = top + 20
#         # display(final_move_list.iloc[top:bot,])
#         # print(df_du_thua[df_du_thua['gcas']==80755744])
#         # print("--- DANH SÁCH VỊ TRÍ CẦN MOVE (LOGIC LÀM TRÒN XUỐNG DÙNG VÒNG LẶP) ---")
#         # print(final_move_list[final_move_list['gcas']==80755744])
#         return final_move_list