import re
import logging
import datetime
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from models.table.tablename_database import TableNameMasterdata
from utils.state_utils import get_state_everywhere

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterdataModel:
    def __init__(self):
        self.obj_master_data = TableNameMasterdata()

    def process_file_masterdata(self, linkfile_masterdata):
        df_master_data = pd.read_excel(linkfile_masterdata)
        # delete 2 rows last
        last_row = len(df_master_data)
        df_master_data = df_master_data.drop([last_row - 2, last_row - 1])
        #chuyển tên cột về chữ thường, khoảng trắng và thay thế "-" thành "_"
        df_master_data.columns = [re.sub(r'[ -]', "_", string).lower().strip() for string in df_master_data.columns]
        df_master_data.columns = [re.sub(r'[.]', "", string) for string in df_master_data.columns]
        #loại bỏ dấu "." trong cột pallet pattern
        #process
        df_master_data['cat'] = df_master_data['cat'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['type1'] = df_master_data['type1'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['type2'] = df_master_data['type2'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['source'] = df_master_data['source'].apply(lambda string: str(string).lower().strip())

        #Lấy user và ngày giờ create
        state = get_state_everywhere()
        user = state.get('username', None)
        # Lấy ngày giờ hiện tại
        current_datetime = datetime.datetime.now()
        # Định dạng đối tượng datetime thành chuỗi
        formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        #thêm user và datetime và df_masterdata
        df_master_data['created_at'] = formatted_string
        df_master_data['user'] = user

        return df_master_data

    def save_masterdata(self, linkfile_masterdata: List) -> Tuple[bool, int]:
        """Lưu file inventory vào database
        Args:
            df: DataFrame tổng hợp của EO, FG, RPM đã được xử lý done
        Returns:
            Boolean indicating success
        """
        try:
            self.df_current = self.process_file_masterdata(linkfile_masterdata)
            number_row_insert = self.obj_master_data.insert_dataframe_new_only(self.df_current)
            logger.info(f"Saved {number_row_insert} inventory records to database")
            return True, number_row_insert
        except Exception as e:
            logger.error(f"Error saving inventory data: {e}")
            return False, 0