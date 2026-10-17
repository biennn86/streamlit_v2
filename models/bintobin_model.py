import logging
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

from models.inventory_model import InventoryModel

from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT, ImportFileStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImportBtbResult:
    def __init__(self, status: ImportFileStatus, data = None, error_message=None):
        self.status = status  
        self.data = data                
        self.error_message = error_message

class BintobinModel:
    def __init__(self, inventory: InventoryModel):
        self.inventory_model = inventory

    def real_file_import_inv_csv(self, link_file_inv_csv) -> pd.DataFrame:
        #Trong phương thức _read_file_inv_prime() đã có hàm validate file tồn kho có phải tồn kho của Prime
        try:
            self.df_inv_csv = self.inventory_model._read_file_inv_prime(link_file_inv_csv)
            return ImportBtbResult(
                    status=ImportFileStatus.SUCCESS,
                    data = self.df_inv_csv
                    )
        except ValueError as val_error:
            # ĐÂY LÀ NƠI HỨNG LỖI INVALID FILE TẬP TRUNG
            # Bất kỳ file nào trong vòng lặp bị lỗi cấu trúc cột, nó sẽ nhảy ngay lập tức vào đây. Kể cả ValueError trong chương trình con
            # Giúp ngắt toán tử concat phía dưới, không làm sập phần mềm.
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            # Hứng các lỗi hệ thống bất ngờ khác (mất kết nối, file hỏng nặng...)
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )

    def real_file_import_inv_excel(self, link_file_inv_csv) -> pd.DataFrame:
        try:
            self.df_inv_csv = self.inventory_model._read_file_inv_excel_prime(link_file_inv_csv)
            return ImportBtbResult(
                    status=ImportFileStatus.SUCCESS,
                    data = self.df_inv_csv
                    )
        except ValueError as val_error:
            # ĐÂY LÀ NƠI HỨNG LỖI INVALID FILE TẬP TRUNG
            # Bất kỳ file nào trong vòng lặp bị lỗi cấu trúc cột, nó sẽ nhảy ngay lập tức vào đây. Kể cả ValueError trong chương trình con
            # Giúp ngắt toán tử concat phía dưới, không làm sập phần mềm.
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            # Hứng các lỗi hệ thống bất ngờ khác (mất kết nối, file hỏng nặng...)
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )

    def read_file_demand(self, link_file_demand) -> pd.DataFrame:
        try:
            try:
                selected_sheets  = pd.read_excel(link_file_demand, sheet_name=["DEMAND EXPORT", "CTMZ,PDS,ST"])
            except:
                raise ValueError(f"File được chọn không phải là file Demand")
            
            dict_demand = {}
            for key in selected_sheets.keys():
                df_export = selected_sheets[key] #CTMZ,PDS,ST
                df = self._get_demand_sheet_by_sheet(df_export)

                if key in ["DEMAND EXPORT"]:
                    key_dict = "demand_export"
                elif key in ["CTMZ,PDS,ST"]:
                    key_dict = "demand_pds"

                dict_demand[key_dict] = df

            return ImportBtbResult(
                status=ImportFileStatus.SUCCESS,
                data = dict_demand,
            )
        except ValueError as val_error:
            # ĐÂY LÀ NƠI HỨNG LỖI INVALID FILE TẬP TRUNG
            # Bất kỳ file nào trong vòng lặp bị lỗi cấu trúc cột, nó sẽ nhảy ngay lập tức vào đây. Kể cả ValueError trong chương trình con
            # Giúp ngắt toán tử concat phía dưới, không làm sập phần mềm.
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            # Hứng các lỗi hệ thống bất ngờ khác (mất kết nối, file hỏng nặng...)
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )

    def get_master_location(self) -> pd.DataFrame:
        location = self.inventory_model.get_location()
        return location
    
    def write_item_not_btb(self, no_bin_to_bin_items: List) -> None:
        FILE_PATH = "no_bin_to_bin_log_no_delete.txt"
        if no_bin_to_bin_items is None:
            no_bin_to_bin_items = []
        # 1. Biến list thành chuỗi: "80883962, 67890, 112233"
        csv_string = ", ".join([str(item) for item in no_bin_to_bin_items])
        # 2. Ghi xuống file
        try:
            with open(FILE_PATH, "w", encoding="utf-8") as file:
                file.write(csv_string)
        except FileNotFoundError as err:
            raise f"Lỗi không tìm thấy file txt Item not bin to bin: {err}"

    def read_item_not_btb(self) -> List:
        FILE_PATH = "no_bin_to_bin_log_no_delete.txt"
        # 2. Đọc file
        try:
            with open(FILE_PATH, "r", encoding="utf-8") as file:
                content = file.read()
            # Chuyển ngược chuỗi thành list số nguyên, tự động dọn rác khoảng trắng
            loaded_list = [int(item) for x in content.split(",") if (item := x.strip()).isdigit()]
            loaded_string = ", ".join([str(item) for item in loaded_list])
            return loaded_string
        except FileNotFoundError as err:
            raise f"Lỗi không tìm thấy file txt Item not bin to bin: {err}"

    def get_deamnd_export(self, dict_demand: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        try:
            if (not dict_demand):
                return ImportBtbResult(status=ImportFileStatus.INVALID) #error_message="Không có file nào được tải lên.")

            df_demand_export = dict_demand.get("demand_export", pd.DataFrame()).rename(columns={"sl_demand": "qty_export"})
            df_demand_pds = dict_demand.get("demand_pds", pd.DataFrame()).rename(columns={"sl_demand": "qty_pds"})
            df_demand_export = df_demand_export[df_demand_export["qty_export"] > 0]
            df_demand_export = df_demand_export.groupby(["gcas"]).agg({
                "qty_export": "sum",
                "market": lambda x: " & ".join(x.astype(str).str.strip().unique())
            }).reset_index()

            return ImportBtbResult(
                        ImportFileStatus.SUCCESS,
                        data = df_demand_export
                    )
            
        except ValueError as val_error:
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )
    def process_bintobin_standard(self, df_inventory: pd.DataFrame, dict_demand: Dict[str, pd.DataFrame]) ->pd.DataFrame:
        try:
            #df_inventory.empty and (not dict_demand or all(df.empty for df in dict_demand.values())):
            if (df_inventory is None) and (not dict_demand):
                return ImportBtbResult(status=ImportFileStatus.INVALID, error_message="Không có file nào được tải lên.")
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
            df_inventory = df_inventory[df_inventory['cat_inv']=='FG'].copy()

            # Bước 1: Tính toán tồn kho chi tiết (Tầng 1 riêng và Các tầng cao riêng)
            df_location = location[["location", "location_system_type", "name_warehouse"]]
            df_inventory = pd.merge(df_inventory, df_location, on='location', how='left')
            # Lọc tồn kho chỉ lấy tầng A, WW, LSL để tính tổng tồn kho
            mask_is_t1_ww_lsl = pd.Series(True, df_inventory.index)
            mask_is_t1_ww_lsl &= df_inventory['location_system_type'].isin(["PF"])
            mask_is_t1_ww_lsl &= df_inventory['name_warehouse'].isin(["WH2"])
            df_inv_t1_ww_lsl = df_inventory[mask_is_t1_ww_lsl]
            # Lọc tồn kho chỉ lấy tầng A. Dùng để đi allocate vị trí cần btb
            mask_is_t1 = pd.Series(True, df_inventory.index)
            mask_is_t1 &= df_inventory['location_system_type'].isin(["PF"])
            mask_is_t1 &= df_inventory['name_warehouse'].isin(["WH2"])
            df_inv_t1 = df_inventory[mask_is_t1]
            #Lọc tồn tầng cao để tính chừa pds
            mask_is_hr = pd.Series(True, df_inventory.index)
            mask_is_hr &= df_inventory['location_system_type'].isin(["HR"])
            df_inv_high = df_inventory[mask_is_hr]
            #Lọc tồn ww, lsl để đưa nhưng item không có trong demand nằm ở ww, lsl lên bin cao
            mask_is_ww = pd.Series(True, df_inventory.index)
            mask_is_ww &= df_inventory['location_system_type'].isin(["WW", "LSL"])
            df_inv_ww_lsl = df_inventory[mask_is_ww]

            # Nhóm tổng tồn tầng a của từng item
            df_inv_grp_t1 = df_inv_t1_ww_lsl.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_t1'})
            # Nhóm tổng tồn tầng cao của từng item
            df_inv_grp_high = df_inv_high.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_high'})
            # Bước 2: Gộp tất cả dữ liệu (Tồn kho + Demand) vào một bảng tổng master theo SKU
            # Dùng thuât toán outer merge để không sót bất kỳ SKU nào xuất hiện ở các file
            df_master = pd.merge(df_inv_grp_t1, df_inv_grp_high, on='gcas', how='outer')
            df_master = pd.merge(df_master, df_demand_pds, on='gcas', how='left')
            df_master = pd.merge(df_master, df_demand_export, on='gcas', how='left')
            # Điền giá trị 0 cho các ô trống (NaN). Đây là nhưng dòng chứa item không có trong deamnd
            # Liệt kê các cột chứa số cần xử lý
            numeric_cols = ['gcas', 'inv_t1', 'inv_high', 'qty_pds', 'qty_export']
            # Ép kiểu về dạng số đồng loạt (các ô chứa chữ hoặc khoảng trắng lỗi sẽ biến thành NaN)
            df_master[numeric_cols] = df_master[numeric_cols].apply(pd.to_numeric, errors='coerce')
            # Chỉ fillna và ép kiểu trên các cột số đó
            df_master = df_master.fillna(0).astype('float64')
            # df_master = df_master.fillna(0).infer_objects(copy=False)

            # Bước 3: Tính toán theo Logic tổng kho
            # 3.1. Tính Tổng tồn kho toàn hệ thống
            df_master['total_inv'] = df_master['inv_t1'] + df_master['inv_high']
            # 3.2. Tính toán xem Tổng kho đã đáp ứng đủ PDS chưa, nếu thừa thì còn lại bao nhiêu khả dụng
            df_master['inv_after_pds'] = np.maximum(0, df_master['total_inv'] - df_master['qty_pds'])
            # 3.3. Xác định lượng hàng được phép GIỮ LẠI ở Tầng 1 để xuất Export trong ngày
            # Nó phải thỏa mãn: Không vượt quá tồn Tầng 1, không vượt quá lượng khả dụng sau PDS, và không vượt quá nhu cầu Export
            ''' df_master['inv_after_pds'] trong dòng code dưới chỉ có tác dụng khi tổng kho bị thiếu hàng để đáp ứng cho nhu cầu PDS.
                Nó bảo đảm rằng: Chỉ khi nào tổng kho thực sự có dư sau khi đã trừ hết sạch nhu cầu PDS, thì phần hàng dư đó mới được phép chia cho nhu cầu Export ở Tầng 1
                Inv_After_PDS đóng vai trò như một "cái van an toàn.
                Ví dụ:
                Giả sử thực tế: Inv_T1 = 30, Inv_High = 0. Tổng kho (Total_Inv) = 30.
                Nhu cầu: Qty_pds = 50 (Thiếu hàng), Qty_export = 40.
                Tính toán theo code:
                Inv_After_PDS = max(0, 30 - 50) = 0 (Tổng kho đã cạn kiệt, không còn dư gì cho việc khác).
                Khi tính Keep_T1: np.minimum(Inv_T1, Inv_After_PDS, Qty_export) -> np.minimum(30, 0, 40) -> Kết quả là 0.
                Từ đó, Qty_To_Move = (30 - 0 = 30). (Hệ thống sẽ ra lệnh bốc toàn bộ 30 cái từ Tầng 1 lên Tầng cao để ưu tiên gom hàng đi đóng PDS).
                * Điều gì xảy ra nếu BỎ Inv_After_PDS
                Nếu code chỉ là: np.minimum(Inv_T1, Qty_export) -> np.minimum(30, 40) = 30.
                Hệ thống sẽ hiểu là: "À, Tầng 1 đang có 30 cái, Export cần 40 cái, vậy cho phép giữ lại cả 30 cái này ở Tầng 1 để xuất Export nhé!"
                Hậu quả là sai logic: Vì đã lấy mất 30 cái này đem đi xuất Export, trong khi đơn hàng PDS (vốn được ưu tiên cao hơn) đang bị thiếu hụt thê thảm và không có hàng để đóng
                ***
                "Tôi muốn giữ lại hàng ở Tầng 1 để bán Export, nhưng số lượng giữ lại không được vượt quá số hàng đang có ở Tầng 1,
                không được vượt quá số lượng khách mua, và đặc biệt là không được lấy lạm vào phần hàng phải trả nợ cho khách PDS"
            '''
            df_master['keep_t1'] = np.minimum(
                df_master['inv_t1'], 
                np.minimum(df_master['inv_after_pds'], df_master['qty_export'])
            )
            ''' Thuật toán mới này có một lỗ hổng rất lớn (gọi là "điểm mù") dẫn đến việc chừa hàng thiếu cho PDS, làm hụt hàng vận hành của PDS trên tầng cao
                Lỗ hổng này xảy ra khi Tổng kho đủ cho PDS (Total_Inv >= Qty_pds) nhưng không đủ cho CẢ HAI (PDS + Export), và lượng hàng ở Tầng 1 vô tình "nuốt" mất phần hàng đáng lẽ phải thuộc về PDS.
                Ví dụ thực tế chứng minh lỗ hổng:
                Giả sử bạn có số liệu một SKU như sau:
                • Tồn kho thực tế: Tầng 1 = 10, Tầng cao = 0 -> Total_Inv = 10.
                • Nhu cầu (Demand): PDS cần 8, Export cần 7. (Tổng nhu cầu hệ thống = 15).

                1. Kiểm tra điều kiện của thuật toán mới:

                • Hệ thống so sánh: Total_Inv (10) >= Qty_pds (8).
                • Kết quả: Thỏa mãn! (Tổng kho rõ ràng đủ hàng cho PDS). Hệ thống kích hoạt nhánh 1.

                2. Tính toán lượng giữ lại và lượng chuyển đi:

                • Keep_T1 = np.minimum(Inv_T1, Qty_export) = np.minimum(10, 7) = 7 thùng.
                • Qty_To_Move = Inv_T1 - Keep_T1 = 10 - 7 = 3 thùng.

                3. Hậu quả vận hành thực tế tại Kho:

                • Bạn làm lệnh bốc 3 thùng từ Tầng 1 lên Tầng cao cho PDS. Lúc này Tầng cao có 3 thùng.
                • Bạn để lại 7 thùng dưới Tầng 1 cho Export.
                • KẾT CỤC: Khi đến giờ đóng gói hàng PDS, khu vực Tầng cao chỉ có 3 thùng, trong khi nhu cầu PDS cần tận 8 thùng. PDS bị thiếu hụt nghiêm trọng tận 5 thùng! Trong khi đó, Export dưới Tầng 1 lại thong dong cầm đủ 7 thùng.
                Tại sao lỗ hổng này lại xuất hiện?
                Lỗi nằm ở chỗ thuật toán mới chỉ kiểm tra xem tổng kho có đủ cho riêng một mình PDS hay không, chứ chưa kiểm tra xem sau khi trừ đi PDS thì tổng kho còn lại bao nhiêu cho Export.
                Bản chất của việc Total_Inv >= Qty_pds không đồng nghĩa với việc bạn được phép cho Export lấy trọn vẹn nhu cầu của họ.
                Vì hàng của PDS đang nằm "lẫn" ở Tầng 1 (do Tầng cao bằng 0), nên khi bạn cho Export lấy đủ 7 thùng, Export đã lấy lẹm vào số hàng đáng lẽ phải đưa lên Tầng cao cho PDS.
            '''
            # df_master['keep_t1'] = np.where(
            #     df_master['total_inv'] >= df_master['qty_pds'],
            #     # TRƯỜNG HỢP ĐỦ HÀNG CHO PDS: Giữ lại Tầng 1 tối đa theo nhu cầu Export
            #     np.minimum(df_master['inv_t1'], df_master['qty_export']),
            #     # TRƯỜNG HỢP THIẾU HÀNG CHO PDS: (Áp dụng lại logic phòng thủ ở câu trước)
            #     np.minimum(df_master['inv_t1'], np.minimum(df_master['inv_after_pds'], df_master['qty_export']))
            # )

            # 3.4. Tính Lượng hàng cần bốc từ Tầng 1 lên Tầng cao
            df_master['qty_to_move'] = df_master['inv_t1'] - df_master['keep_t1']
            # Bước 4: Xuất kết quả danh sách lệnh chuyển hàng
            #inv_t1, inv_high, qty_pds,	qty_export,	total_inv, inv_after_pds, keep_t1, qty_to_move
            df_move_action = df_master[df_master['qty_to_move'] > 0] #[['gcas', 'inv_t1', 'keep_t1', 'qty_to_move']]

            # Bước 4. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)
            # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
            df_process = pd.merge(df_inv_t1, df_move_action, on='gcas', how='left')
            # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
            # Việc này giúp ưu tiên giải phóng các location pallet nguyên và ưu tiên lấy hàng HD, QU trước, để hàng RL lại T1 để xuất (tối ưu không gian Bin)
            df_process['date_sort'] = df_process['batch'].str[1:4]
            df_process = df_process.sort_values(by=['gcas', 'date_sort', 'location', 'qty', 'status'], ascending=[True, False, False, False, False]).reset_index(drop=True)
            df_process.drop(columns=['date_sort'], inplace=True)
            
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

            # 4. Xác định item over_demand, not_in_demand hay chừa pds
            inv_high = df_process["inv_high"]
            qty_to_move = df_process["qty_to_move"]
            qty_export = df_process["qty_export"]
            qty_pds = df_process["qty_pds"]
            qty_keep_t1 = df_process["keep_t1"]
            # 4.1. Not in demand
            not_in_demand = (qty_keep_t1 == 0) & (qty_pds == 0) & (qty_export == 0)
            # 4.2. qty_export = 0 và qty_pds > 0 => chỉ giữ pds không xuất export
            keep_pds = (qty_export == 0) & (qty_pds > 0) & (qty_to_move > 0)
            # 4.3. qty_export > 0 và qty_pds = 0 và ty_to_move > 0 => Over demand
            over_demand = (qty_export > 0) & (qty_pds == 0) & (qty_to_move > 0)
            # 4.4. qty_export > 0 và qty_pds > 0 qty_pds < inv_high  => Over demand
            over_demand_keep_pds_done = (qty_export > 0) & (qty_pds > 0) & (qty_pds < inv_high) & (qty_to_move > 0)
            # 4.5. qty_export > 0 và qty_pds > 0 qty_pds > inv_high  => Vừa keep pds vừa xuất export
            keep_pds_and_export = (qty_export > 0) & (qty_pds > 0) & (qty_pds > inv_high) & (qty_to_move > 0)

            conditions = [not_in_demand,
                          keep_pds, over_demand,
                          over_demand_keep_pds_done,
                          keep_pds_and_export]
            lost_pds = qty_pds - inv_high
            choices_name = [
                "Not In Demand",
                "Keep PDS " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Over Demand " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Over Demand " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Holds PDS while exporting. Do not over-export"]
            #"Holds PDS while exporting. Maintain at " + qty_pds.fillna(0).astype(int).astype(str) + " CS, an additional " + lost_pds.fillna(0).astype(int).astype(str) + " CS for bin-to-bin. " + "Do not over-export"
            
            df_process["note_btb"] = np.select(condlist=conditions, choicelist=choices_name, default="Unknown")

            # 5. LỌC KẾT QUẢ CUỐI CÙNG
            df_btb_rack = df_process[df_process['qty_need_move'] > 0].copy()

            # final_move_list = final_move_list[[
            #     'gcas', 'location', 'qty', 'inv_t1', 'inv_high', 'total_inv', 'qty_pds', 'qty_export', 'inv_after_pds', 'keep_t1', 'qty_to_move', 'qty_need_move', 'available', 'location_system_type'
            # ]]

            # 6. LẤY NHỮNG ITEM Ở ĐƯỜNG LUỒNG KHÔNG CÓ TRONG DEMAND
            df_item_not_in_deamnd = df_move_action[(df_move_action["qty_pds"] == 0) & (df_move_action["qty_export"] == 0)]
            df_btb_ww = pd.merge(df_inv_ww_lsl, df_item_not_in_deamnd, on='gcas', how='left')
            df_btb_ww = df_btb_ww[(df_btb_ww["qty_pds"] == 0) & (df_btb_ww["qty_export"] == 0)]
            df_btb_ww["note_btb"] = "Not In Demand"
            # 6. GỘP 2 DATAFRAME BIN TO BIN RACK VÀ WW
            df_btb_final = pd.concat([df_btb_rack, df_btb_ww], ignore_index=True)

            return ImportBtbResult(
                        ImportFileStatus.SUCCESS,
                        data = df_btb_final
                    )
        except ValueError as val_error:
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )

    def process_bintobin_greedy(self, df_inventory: pd.DataFrame, dict_demand: Dict[str, pd.DataFrame]) ->pd.DataFrame:
        try:
            if (df_inventory is None) and (not dict_demand):
                return ImportBtbResult(status=ImportFileStatus.INVALID, error_message="Không có file nào được tải lên.")
            #Version mới nhất
            # Chiến thuật này tính chừa PDS trên tồn kho tầng cao. Ưu tiên chừa PDS là tối thường và 100% hàng PDS phải đưa lên tầng cao. Thuật toán tham lam
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
            mask_is_t1 &= df_inventory['location_system_type'].isin(["PF"])
            mask_is_t1 &= df_inventory['name_warehouse'].isin(["WH2"])
            df_inv_t1 = df_inventory[mask_is_t1]
            #Lọc tồn tầng cao để tính chừa pds
            mask_is_hr = pd.Series(True, df_inventory.index)
            mask_is_hr &= df_inventory['location_system_type'].isin(["HR"])
            df_inv_high = df_inventory[mask_is_hr]
            #Lọc tồn ww, lsl để đưa nhưng item không có trong demand nằm ở ww, lsl lên bin cao
            mask_is_ww = pd.Series(True, df_inventory.index)
            mask_is_ww &= df_inventory['location_system_type'].isin(["WW", "LSL"])
            df_inv_ww_lsl = df_inventory[mask_is_ww]

            # Nhóm tổng tồn tầng a của từng item
            df_inv_grp_t1 = df_inv_t1.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_t1'})
            # Nhóm tổng tồn tầng cao của từng item
            df_inv_grp_high = df_inv_high.groupby('gcas', as_index=False)['qty'].sum().rename(columns={'qty': 'inv_high'})
            # Bước 2: Gộp tất cả dữ liệu (Tồn kho + Demand) vào một bảng tổng master theo SKU
            # Dùng thuât toán outer merge để không sót bất kỳ SKU nào xuất hiện ở các file
            df_master = pd.merge(df_inv_grp_t1, df_inv_grp_high, on='gcas', how='outer')
            df_master = pd.merge(df_master, df_demand_pds, on='gcas', how='left')
            df_master = pd.merge(df_master, df_demand_export, on='gcas', how='left')
            # Điền giá trị 0 cho các ô trống (NaN). Đây là nhưng dòng chứa item không có trong deamnd
            # Liệt kê các cột chứa số cần xử lý
            numeric_cols = ['gcas', 'inv_t1', 'inv_high', 'qty_pds', 'qty_export']
            # Ép kiểu về dạng số đồng loạt (các ô chứa chữ hoặc khoảng trắng lỗi sẽ biến thành NaN)
            df_master[numeric_cols] = df_master[numeric_cols].apply(pd.to_numeric, errors='coerce')
            # Chỉ fillna và ép kiểu trên các cột số đó
            df_master = df_master.fillna(0).astype('float64')
            # df_master = df_master.fillna(0).infer_objects(copy=False)

            # Bước 2: Tính lượng PDS còn THIẾU trên tầng cao cần phải bù vào
            df_master['pds_needed_high'] = np.maximum(0, df_master['qty_pds'] - df_master['inv_high'])
            # Bước 3: Tính lượng tồn Tầng 1 còn lại sau khi đã ưu tiên cất đi để bù vào PDS trên tầng cao
            df_master['t1_available_after_pds'] = np.maximum(0, df_master['inv_t1'] - df_master['pds_needed_high'])
            # Bước 4: Lượng thực tế GIỮ LẠI ở Tầng 1 để xuất hàng trong ngày (Export)
            df_master['keep_t1'] = np.minimum(df_master['t1_available_after_pds'], df_master['qty_export'])
            # Bước 5: Lượng hàng bốc từ Tầng 1 lên tầng cao (Bao gồm PDS thiếu + Tồn thừa export)
            df_master['qty_to_move'] = df_master['inv_t1'] - df_master['keep_t1']
            df_move_action = df_master[df_master['qty_to_move'] > 0] #[['gcas', 'inv_t1', 'keep_t1', 'qty_to_move']]
            # Bước 6. THUẬT TOÁN TRỪ LÙI LÀM TRÒN XUỐNG (TỐI ƯU TỐC ĐỘ BẰNG MẢNG)
            # Gộp dữ liệu tổng vào chi tiết vị trí và chỉ lấy các vị trí thuộc Tầng A
            df_process = pd.merge(df_inv_t1, df_move_action, on='gcas', how='left')
            # QUAN TRỌNG: Sắp xếp tồn kho tăng dần theo GCAS và QTY 
            # Việc này giúp ưu tiên giải phóng các location pallet nguyên và ưu tiên lấy hàng HD, QU trước, để hàng RL lại T1 để xuất (tối ưu không gian Bin)
            df_process['date_sort'] = df_process['batch'].str[1:4]
            df_process = df_process.sort_values(by=['gcas', 'date_sort', 'location', 'qty', 'status'], ascending=[True, False, False, False, False]).reset_index(drop=True)
            df_process.drop(columns=['date_sort'], inplace=True)

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

            # 4. Xác định item over_demand, not_in_demand hay chừa pds
            inv_high = df_process["inv_high"]
            qty_to_move = df_process["qty_to_move"]
            qty_export = df_process["qty_export"]
            qty_pds = df_process["qty_pds"]
            qty_keep_t1 = df_process["keep_t1"]
            # 4.1. Not in demand
            not_in_demand = (qty_keep_t1 == 0) & (qty_pds == 0) & (qty_export == 0)
            # 4.2. qty_export = 0 và qty_pds > 0 => chỉ giữ pds không xuất export
            keep_pds = (qty_export == 0) & (qty_pds > 0) & (qty_to_move > 0)
            # 4.3. qty_export > 0 và qty_pds = 0 và ty_to_move > 0 => Over demand
            over_demand = (qty_export > 0) & (qty_pds == 0) & (qty_to_move > 0)
            # 4.4. qty_export > 0 và qty_pds > 0 qty_pds < inv_high  => Over demand
            over_demand_keep_pds_done = (qty_export > 0) & (qty_pds > 0) & (qty_pds < inv_high) & (qty_to_move > 0)
            # 4.5. qty_export > 0 và qty_pds > 0 qty_pds > inv_high  => Vừa keep pds vừa xuất export
            keep_pds_and_export = (qty_export > 0) & (qty_pds > 0) & (qty_pds > inv_high) & (qty_to_move > 0)

            conditions = [not_in_demand,
                            keep_pds, over_demand,
                            over_demand_keep_pds_done,
                            keep_pds_and_export]
            lost_pds = qty_pds - inv_high
            choices_name = [
                "Not In Demand",
                "Keep PDS " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Over Demand " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Over Demand " + qty_to_move.fillna(0).astype(int).astype(str) + " CS",
                "Holds PDS while exporting. Do not over-export"]
            
            df_process["note_btb"] = np.select(condlist=conditions, choicelist=choices_name, default="Unknown")



            # 4. LỌC KẾT QUẢ CUỐI CÙNG
            df_btb_rack = df_process[df_process['qty_need_move'] > 0].copy()

            # final_move_list = final_move_list[[
            #     'gcas', 'location', 'qty', 'inv_t1', 'inv_high', 'total_inv', 'qty_pds', 'qty_export', 'inv_after_pds', 'keep_t1', 'qty_to_move', 'qty_need_move', 'available', 'location_system_type'
            # ]]

            # 5. LẤY NHỮNG ITEM Ở ĐƯỜNG LUỒNG KHÔNG CÓ TRONG DEMAND
            df_item_not_in_deamnd = df_move_action[(df_move_action["qty_pds"] == 0) & (df_move_action["qty_export"] == 0)]
            df_btb_ww = pd.merge(df_inv_ww_lsl, df_item_not_in_deamnd, on='gcas', how='left')
            df_btb_ww = df_btb_ww[(df_btb_ww["qty_pds"] == 0) & (df_btb_ww["qty_export"] == 0)]
            df_btb_ww["note_btb"] = "Not In Demand"
            # 6. GỘP 2 DATAFRAME BIN TO BIN RACK VÀ WW LẠI
            df_btb_final = pd.concat([df_btb_rack, df_btb_ww], ignore_index=True)

            return ImportBtbResult(
                ImportFileStatus.SUCCESS,
                data = df_btb_final
            )
        except ValueError as val_error:
            return ImportBtbResult(
                status=ImportFileStatus.INVALID,
                error_message=f"Xử lý thất bại! Lý do: {str(val_error)}"
            )
        except Exception as e:
            return ImportBtbResult(
                status=ImportFileStatus.SYSTEM_ERROR,
                error_message=f"Lỗi hệ thống chưa xác định: {str(e)}"
            )
    

    def _get_demand_sheet_by_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        # CHUẨN HÓA DỮ LIỆU ĐỂ TÌM KIẾM (Tránh tạo bản sao lớn bằng cách xử lý trực tiếp)
        df_upper = df.astype(str).apply(lambda x: x.str.strip().str.upper())

        # VALIDATE 1: Tìm cột 'SKU' an toàn
        sku_mask = df_upper == "SKU"
        sku_positions = np.where(sku_mask.any(axis=0))[0]
        if len(sku_positions) == 0:
            raise ValueError(
                "Không tìm thấy cột chứa từ khóa 'SKU' trong file dữ liệu."
            )
        sku_col_idx = sku_positions[0]

        # VALIDATE 2: Tìm cột 'CON LAI/CÒN LẠI' an toàn
        con_lai_mask = df_upper.apply(
            lambda x: x.str.contains("CON LAI|CÒN LẠI", regex=True)
        )
        con_lai_positions = np.where(con_lai_mask.any(axis=0))[0]
        if len(con_lai_positions) == 0:
            raise ValueError(
                "Không tìm thấy cột chứa từ khóa 'CON LAI' hoặc 'CÒN LẠI'."
            )
        con_lai_col_idx = con_lai_positions[0]

        # VALIDATE 3: Kiểm tra giới hạn cột Market (SKU + 2)
        market_col_idx = sku_col_idx + 2
        if market_col_idx >= df.shape[1]:
            raise IndexError(
                f"Cột Market tính toán (chỉ số {market_col_idx}) vượt quá số cột hiện có của file."
            )

        # 4. Trích xuất tên Market an toàn (Dùng shift(-1) chuẩn hóa thành boolean)
        is_next_row_sku = (
            sku_mask.iloc[:, sku_col_idx].shift(-1).fillna(False).astype(bool)
        )
        df["Market"] = np.where(
            is_next_row_sku, df.iloc[:, market_col_idx], np.nan
        )

        # Điền Market xuống dưới
        df["Market"] = df["Market"].ffill()

        # 5. Khởi tạo DataFrame kết quả
        result_df = pd.DataFrame(
            {
                "Market": df["Market"],
                "SKU": df.iloc[:, sku_col_idx],
                "sl_demand": df.iloc[:, con_lai_col_idx],
            }
        )

        # VALIDATE 4: Lọc sạch SKU (Chỉ giữ dòng là chữ số và loại bỏ NaN/Khoảng trắng)
        result_df["SKU_clean"] = result_df["SKU"].astype(str).str.strip()
        final_df = result_df[result_df["SKU_clean"].str.isdigit()].copy()

        # Nếu sau khi lọc không còn dữ liệu -> Validate lỗi cấu trúc dòng
        if final_df.empty:
            print(
                "Cảnh báo: Không có dòng dữ liệu SKU hợp lệ (dạng số) nào được tìm thấy."
            )

        # 6. Định dạng lại đầu ra
        final_df = final_df[["SKU", "sl_demand", "Market"]]
        final_df = final_df.rename(columns={"SKU": "gcas", "Market": "market"})

        return final_df

        #================================================
        # # ĐOẠN CODE CŨ CHƯA VALIDATE
        # # 1. Đọc toàn bộ file Excel
        # #1. Đọc file
        # # df = selected_sheets["DEMAND EXPORT"]

        # # 2. Tìm vị trí cột chứa chữ 'SKU' (Lấy phần tử đầu tiên của tuple)
        # sku_mask = df.astype(str).apply(lambda x: x.str.strip().str.upper()) == 'SKU'
        # sku_col_idx = np.where(sku_mask.any(axis=0))[0][0]

        # # 3. Tìm vị trí cột chứa chữ 'CON LAI/CÒN LẠI'
        # con_lai_mask = df.astype(str).apply(lambda x: x.str.strip().str.upper().str.contains('CON LAI|CÒN LẠI', regex=True))
        # con_lai_col_idx = np.where(con_lai_mask.any(axis=0))[0][0]

        # # Tọa độ cột Market = Cột SKU dịch sang phải 2 ô (Hết lỗi TypeError)
        # market_col_idx = sku_col_idx + 2

        # # 4. Trích xuất tên Market (Đã sửa lỗi FutureWarning bằng .astype(bool))
        # is_next_row_sku = sku_mask.iloc[:, sku_col_idx].shift(-1).astype(bool).fillna(False)
        # df['Market'] = np.where(is_next_row_sku, df.iloc[:, market_col_idx], np.nan)

        # # Dùng ffill() để điền tên Market xuống các dòng dưới
        # df['Market'] = df['Market'].ffill()

        # # 5. Gộp dữ liệu thành bảng kết quả mới bằng cách chỉ định chỉ số cột cụ thể
        # result_df = pd.DataFrame({
        #     'Market': df['Market'],
        #     'SKU': df.iloc[:, sku_col_idx],
        #     'sl_demand': df.iloc[:, con_lai_col_idx]
        # })

        # # 6. Lọc sạch dữ liệu: Chỉ giữ dòng có SKU là chữ số
        # result_df['SKU_clean'] = result_df['SKU'].astype(str).str.strip()
        # final_df = result_df[result_df['SKU_clean'].str.isdigit() == True].copy()

        # # Giữ lại đúng 3 cột cần thiết theo yêu cầu
        # final_df = final_df[['SKU', 'sl_demand', 'Market']]
        # final_df = final_df.rename(columns={
        #     'SKU': 'gcas',
        #     'Market': 'market'
        # })

        # # Hiển thị kết quả kiểm tra
        # return final_df
        #=================================================

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