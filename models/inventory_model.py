import datetime
import streamlit as st
import logging
from typing import List, Tuple, Dict, Any, Optional
import re 
import pandas as pd
import numpy as np
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT
from io import StringIO
from models.table.tablename_database import *
from utils.state_utils import get_state_everywhere



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InventoryModel:
    """Model phân tích tổng hợp data cho dashboard"""
    def __init__(self):
        self.inventory = TableNameInventory()
        self.location = TableNameLocation()
        self.masterdata = TableNameMasterdata()

        #Tạo df location, và masterdata để lưu data và ram
        #Mục đích để chỉ chạy get data 1 lần, lần sau chạy check biến khác rỗng sẽ lấy
        #data trên ram trả về
        self.df_location = pd.DataFrame()
        self.df_masterdata = pd.DataFrame()
        self.df_current = pd.DataFrame()
    
    def process_inventory(self, uploaded_files: List) -> pd.DataFrame:
        """
        Chuyển đổi nội dung 3 file FG, RPM, EO thành DataFrame
        """
        list_df = []
        CAT_FG = ValidateFile.CATEGORY_FG.value
        dict_data_rpmfgeo = self._cover_multifile_todict(uploaded_files)
        isvalid = self._validate_files(dict_data_rpmfgeo)
        if isvalid:
            for key, value in dict_data_rpmfgeo.items():
                if Pattern.DOT.value in key:
                    duoi_file = re.split(Pattern.DOT_PATTERN.value, key)[-1]
                else:
                    duoi_file = None

                if duoi_file in ValidateFile.LIST_DUOI_FILE_EO.value:
                    list_df.append(self._read_file_eo(value))
                    #import description EO to masterdata in database
                    self.import_masterdata_eo_to_masterdata_db(value)
                else:
                    cat_file = re.search(Pattern.CATEGORY_FILE.value, value.getvalue(), re.MULTILINE).group()
                    if cat_file in CAT_FG:
                        date_time = re.search(Pattern.GET_DATETIME.value, value.getvalue(), re.MULTILINE).group().rstrip()
                    list_df.append(self._read_fg_rpm_file(value))

        if list_df is not None:
            df_data_final = pd.concat(list_df, ignore_index=True)
            #Chèn thêm cột datetime ở vị trí đầu tiên trong df
            df_data_final.insert(0, 'date', date_time)
            #lấy user
            state = get_state_everywhere()
            user = state.get('username', None)
            # Lấy ngày giờ hiện tại
            current_datetime = datetime.datetime.now()
            # Định dạng đối tượng datetime thành chuỗi
            formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            df_data_final['created_at'] = formatted_string
            df_data_final['user'] = user
            logger.info(f"Processed {len(df_data_final)} inventory records")
            return df_data_final
        else:
            logger.error(f"Processed read inventory error")
            return None
        
    def save_inventory(self, uploaded_files: List) -> Tuple[bool, int, Optional[pd.DataFrame]]:
        """Lưu file inventory vào database
        Args:
            df: DataFrame tổng hợp của EO, FG, RPM đã được xử lý done
        Returns:
            Boolean indicating success
        """
        try:
            self.df_current = self.process_inventory(uploaded_files)
            number_row_insert = self.inventory.insert_dataframe_new_only(self.df_current)
            logger.info(f"Saved {len(self.df_current)} inventory records to database")
            return True, number_row_insert, self.df_current
        except Exception as e:
            logger.error(f"Error saving inventory data: {e}")
            return False, 0, pd.DataFrame()
        
    def import_masterdata_eo_to_masterdata_db(self, df_eo: pd.DataFrame) -> None:
        """ Thêm cột type1 là EO để phân biệt với masterdata RPM
            Thêm cột quy cách 'bd_plt_pat' là 9999 để lọc trùng data của sql được chạy chính xác
            Vì trong sql cột NULL với NULL trả về FALSE, nên khi insert vào sẽ bị trùng data
            Chi tiết đọc method insert_dataframe() để hiểu hơn.
        """
        try:
            name_columns_masterdata = ['gcas', 'description', 'cat', 'type1', 'type2', 'vendor_name', 'source', 'jit', 'bd_plt_pat', 'history_storeLocation', 'latest_gr', 'created_at', 'user']
            df_masterdata_eo = pd.DataFrame(columns=name_columns_masterdata)
            df_eo_import = df_eo.copy(deep=True)
            df_eo_import.columns = [re.sub("[ -]", "_", string).lower().strip() for string in df_eo_import.columns]

            df_masterdata_eo['gcas'] = df_eo_import['gcas']
            df_masterdata_eo['description'] = df_eo_import['description']
            df_masterdata_eo['cat'] = df_eo_import['supply_chain']
            df_masterdata_eo['type1'] = 'eo'
            df_masterdata_eo['bd_plt_pat'] = 9999
            df_masterdata_eo['type2'] = df_eo_import['type']

            #lấy user
            state = get_state_everywhere()
            user = state.get('username', None)
            # Lấy ngày giờ hiện tại
            current_datetime = datetime.datetime.now()
            # Định dạng đối tượng datetime thành chuỗi
            formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            df_masterdata_eo['created_at'] = formatted_string
            df_masterdata_eo['user'] = user

            result = self.masterdata.insert_dataframe_new_only(df_new=df_masterdata_eo)
            logger.info(f"Insert {result} masterdata EO to database")
        except Exception as e:
            raise e
        
    def get_inventory_data(self, date_time: Optional[str]=None) -> pd.DataFrame:
        """ 1. Lấy df vừa xử lý khi import file hay là df current
            2. Nếu df_current rỗng thì trích xuất inventory lần import gần nhất trong database
            3. Nếu date_time được truyền thì lấy df theo ngày date_time được truyền trong database

            Return: DataFrame inventory
        """
        try:
            if not self.df_current.empty:
                return self.df_current
            else:
                df = self.inventory.read_inventory_by_datetime(date_time)
                logger.info(f"Retrieved {len(df)} inventory records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving inventory data: {e}")
            return pd.DataFrame()
    
    def get_masterdata(self) -> pd.DataFrame:
        """Lấy Masterdata trong database
        Returns:
            DataFrame Masterdataa
        """
        try:
            if self.df_masterdata.empty:
                self.df_masterdata = self.masterdata.read_to_dataframe()
                self.df_masterdata = self.df_masterdata[Columns.COLUMNS_MASTERDATA_NEED.value]
                logger.info(f"Retrieved {len(self.df_masterdata)} masterdata records from database")
                return self.df_masterdata
            else:
                return self.df_masterdata
        except Exception as e:
            logger.error(f"Error retrieving masterdata data: {e}")
            return pd.DataFrame()
        
    def get_location(self) -> pd.DataFrame:
        """Lấy Masterdata trong database
        Returns:
            DataFrame Masterlocation
        """
        try:
            if self.df_location.empty:
                self.df_location = self.location.read_to_dataframe()
                logger.info(f"Retrieved {len(self.df_location)} location records from database")
                return self.df_location
            else:
                return self.df_location
        except Exception as e:
            logger.error(f"Error retrieving location data: {e}")
            return pd.DataFrame()
        
    
    def get_merge_data(self, date_time: Optional[str]=None)-> pd.DataFrame:
        """ Merge data của inventory, location, masterdata
            Có thể truyền vào string date_time được chọn từ streamlit
        Returns:
            DataFrame đã merge
        """
        try:
            df_inventory = self.get_inventory_data(date_time)
            df_location = self.get_location()
            df_masterdata = self.get_masterdata()

            # df_inventory['gcas'] = pd.to_numeric(df_inventory['gcas'], downcast='integer')
            df_inventory['gcas'] = df_inventory['gcas'].astype('int64')
            df_inventory['pallet'] = pd.to_numeric(df_inventory['pallet'], downcast='integer')
            df_inventory['qty'] = pd.to_numeric(df_inventory['qty'], downcast='float')
            df_inventory['batch'] = df_inventory['batch'].astype(str)
            df_inventory['vnl'] = df_inventory['vnl'].astype(str)

            #chuyển kiểu dữ liệu cột gcas trong masterdata về int. Kiểu mặc định đang là obj
            # df_masterdata['gcas'] = pd.to_numeric(df_masterdata['gcas'], downcast='integer')
            df_masterdata['gcas'] = df_masterdata['gcas'].astype('int64')
            #khi update master data dùng method append để lấy được lịch sử thay đổi thông tin của gas (ví dụ như pallet pattern)
            #nên khi lấy master data ra phân tích phải loại bỏ trùng để tránh duplicate data đi merge.
            #khi dropduplicate giữ lại dòng cuối cùng để lấy thông tin data mới nhất
            df_masterdata = df_masterdata.drop_duplicates(subset=['gcas'], keep='last')
            
            # merge data của tồn kho, location, master data
            df_inv_mt = pd.merge(left=df_inventory, right=df_masterdata, left_on='gcas', right_on='gcas', how='left' )
            df_inv_mt_loc = pd.merge(left=df_inv_mt, right=df_location, left_on='location', right_on='location', how='left') #suffixes=('_inv', '_loc')
            df_inv_mt_loc['pallet_capacity'] = pd.to_numeric(df_inv_mt_loc['pallet_capacity'], downcast='integer')
            df_inv_mt_loc['gcas'] = df_inv_mt_loc['gcas'].astype(str)
            df_final = df_inv_mt_loc

            # df_final.to_excel('data_tonghop.xlsx', index=False)
            logger.info(f"Merged {len(df_final)} records inventory, location, masterdata")
            
            return df_final
        except Exception as e:
            logger.error(f"Error merge data: {e}")
            return pd.DataFrame()
        

    def _cover_multifile_todict(self, uploaded_files: List) -> Dict[str, Any]:
        '''
        uploaded_files ở dạng list chứa obj của các file import.
        Chuyển file import thành dict. Key chứa tên file, value chứa value data
        Chỉ lấy 3 file cuối trong uploaded_files, khi user import nhiều file chưa clear cache được
        '''
        dict_files_data_soucre = {}
        get_3_last_file = uploaded_files[len(uploaded_files) - 3:]
        for file in get_3_last_file:
            if Pattern.DOT.value in file.name:
                duoifile = re.split(Pattern.DOT_PATTERN.value, file.name)[-1]
            else:
                duoifile = None
                
            if duoifile in ValidateFile.LIST_DUOI_FILE_EO.value:
                try:
                    data = pd.read_excel(file)
                    dict_files_data_soucre.update({file.name: data})
                except:
                    pass
            elif duoifile in ValidateFile.LIST_DUOI_FILE_TXT.value:
                data_txt = StringIO(file.getvalue().decode(ValidateFile.DECODE_FILE_TXT.value))
                dict_files_data_soucre.update({file.name: data_txt})
        return dict_files_data_soucre
    
    def _validate_files(self, dict_data_rpmfgeo: Dict[str, Any]) -> bool:
        """
        Xác định file import eo có phải đuôi excel không và các cột có trùng với cột của file eo không
        Xác định nội dung bên trong file txt có chưa ký tự FG và RPM không
        """
        regex_find_dot = re.compile(Pattern.DOT_PATTERN.value)
        regex_catfile = re.compile(Pattern.CATEGORY_FILE.value, re.MULTILINE)
        columns_eo = Columns.COLUMNS_FILE_EO.value
        IS_FILE_EO = False; IS_FILE_FG = False; IS_FILE_RPM = False
        #1: Check nội dung bên trong của từng file
        for key, value in dict_data_rpmfgeo.items():
            if Pattern.DOT.value in key:
                match_dot = regex_find_dot.split(key)
                duoi_file = match_dot[-1]
                if duoi_file in ValidateFile.LIST_DUOI_FILE_EO.value:
                    try:
                        df_eo_check_columns = value.copy()
                        df_eo_check_columns.columns = [re.sub("[ -]", "_", string).lower().strip() for string in df_eo_check_columns.columns]
                        columns_crr_file = df_eo_check_columns.columns.to_list()
                        if columns_eo == columns_crr_file:
                            IS_FILE_EO = True
                    except:
                        IS_FILE_EO = False
                else:
                    cls_file = regex_catfile.findall(value.getvalue())
                    if cls_file == ValidateFile.CATEGORY_FG.value:
                        IS_FILE_FG = True
                    elif cls_file == ValidateFile.CATEGORY_RPM.value:
                        IS_FILE_RPM = True
            else:
                cls_file = regex_catfile.findall(value.getvalue())
                if cls_file == ValidateFile.CATEGORY_FG.value:
                    IS_FILE_FG = True
                elif cls_file == ValidateFile.CATEGORY_RPM.value:
                    IS_FILE_RPM = True

        if IS_FILE_EO and IS_FILE_FG and IS_FILE_RPM:
            return True
        else:
            return False
        
    def _read_fg_rpm_file(self, data: str) -> pd.DataFrame:
        LEN_RPM_LOST_VNL = ValidateFile.LEN_RPM_LOST_VNL.value
        LEN_LINE_FINAL = ValidateFile.LEN_LINE_FINAL.value
        #option 1: ^(?=\s*[0-9]{8})(.+)(?<=NONE) -> không lấy được dòng không có gcas và có batch bắt đầu bằng chữ
        #option 2:  ^(?=\s*).+(?<=NONE) -> lấy được tất cả các dòng thõa mãn điều kiện
        #option 3: ^(?:.+)(?<=NONE)(?:\b){0} -> lấy được tất cả các dòng thõa mãn điều kiện và tốc độ tính toán nhanh hơn
        pattern_getline_tonkho = re.compile(Pattern.GET_TONKHO.value, re.MULTILINE)
        pt_class_file = re.compile(Pattern.CATEGORY_FILE.value,  re.MULTILINE)
        get_data_StringIO = data.getvalue()
        conten = pattern_getline_tonkho.findall(get_data_StringIO)
        #Xác định file đang đọc là F hay P
        match_cls_file = pt_class_file.search(get_data_StringIO)
        if match_cls_file is not None:
            cls_match = match_cls_file.group()
        else:
            cls_match = None

        list_data = []
        for line in conten:
            try:
                # check_line_get = pattern_getline_tonkho.match(line)
                # if check_line_get:
                #     data_line = check_line_get.group()
                
                data_line_clear_vn07 = re.sub(Pattern.VN07.value, "", line)
                data_line_clear_two_space = re.sub(Pattern.TWO_SPACE.value, ";", data_line_clear_vn07)
                scile = re.search(Pattern.STATUS.value, data_line_clear_two_space).span()[0]
                data_line_left = data_line_clear_two_space[:scile]
                data_line_right = data_line_clear_two_space[scile:]
                data_line_left =  re.sub(Pattern.ONE_SPACE.value, ";", data_line_left)
                data_line_right =  re.sub(Pattern.ONE_SPACE.value, "", data_line_right)
                data_line_final = data_line_left + data_line_right
                data_line_final = data_line_final.split(";")
                
            
                if (cls_match in ValidateFile.CATEGORY_FG.value):
                    data_line_final.insert(2, VNL_CAT.VNL_FG.value)
                    data_line_final.append(VNL_CAT.FG.value)

                if (cls_match in ValidateFile.CATEGORY_RPM.value):
                    if (len(data_line_final) == LEN_RPM_LOST_VNL):
                        data_line_final.insert(2, VNL_CAT.RPM_LOST_VNL.value)
                        data_line_final.append(VNL_CAT.RPM.value)
                    else:
                        data_line_final.append(VNL_CAT.RPM.value)

                len_lst_final = len(data_line_final)
                if (list_data == []) and (len_lst_final == LEN_LINE_FINAL):
                    list_data.append(data_line_final)
                elif len_lst_final == LEN_LINE_FINAL:
                    current_first_number = len(data_line_final[0])
                    if current_first_number == 0:
                        data_line_final[0] = list_data[-1][0]
                        list_data.append(data_line_final)
                    else:
                        list_data.append(data_line_final)
            except Exception as e:
                print(f'Lỗi đọc file txt: {str(e)}')
        
        df_data = self._create_df_tonkho_from_list(list_data)
        return df_data

    def _create_df_tonkho_from_list(self, data: List[List]) -> pd.DataFrame:
        columns_inv = Columns.COLUMNS_INV.value
        df_data = pd.DataFrame(data, columns = columns_inv)
        df_data = df_data.astype('string')
        return df_data
    
    def _read_file_eo(self, df_eouploaded: pd.DataFrame) -> pd.DataFrame:
        df_eo = df_eouploaded.copy()
        # df_eo = pd.read_excel(link_file)
        columns_eo = Columns.COLUMNS_INV.value
        df_eo = df_eo[Columns.COLUMNS_EO_NEED.value]
        df_eo['Bin'] = df_eo['Bin'].apply(lambda x: re.sub(r'[ ]', '', x.upper()))
        df_eo.insert(3, 'status', 'RL')
        df_eo.insert(5, 'pallet', 1)
        df_eo.insert(8, 'cat_inv', 'EO')
        df_eo.columns = columns_eo
        df_eo = df_eo.astype('string')
        return df_eo
    
 