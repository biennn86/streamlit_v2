import logging
import re
from pathlib import Path
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT
from models.inventory_model import InventoryModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

'''
from pathlib import Path

file_list = ["report.pdf", "README", "data.csv", "LICENSE", "script.py"]

# Nếu không có đuôi, gán giá trị 'No Extension'
extension_list = [Path(file).suffix if Path(file).suffix else "No Extension" for file in file_list]

print(extension_list)
# Kết quả: ['.pdf', 'No Extension', '.csv', 'No Extension', '.py']
'''

class InventoryController:
    '''
    Controller: xử lý các vấn đề liên quan đến FILE
    Model: xử lý các vấn đề liên quan đến DỮ LIỆU
    '''
    def __init__(self, inventory_model: InventoryModel):
        """Initialize the inventory controller.
        
        Args:
            inventory_model: Instance of the InventoryModel
        """
        self.inventory_model = inventory_model

    def _validate_file(self, uploaded_files: List) -> Tuple[bool, str]:
        """Check đuôi file và số lượng file upload có hợp lệ không
        Returns:
            Tuple[str, str]
        """
        lst_duoi_file_import = [Path(file.name).suffix for file in uploaded_files]
        
        if (len(uploaded_files) == 0):
            return False, f"No file uploaded"
        elif len(lst_duoi_file_import) > 3:
            return False, f"Invalid number of uploaded files"
        # elif len(uploaded_files) % 3 != 0:
        #     return False, f"The number of imported files must be divisible by 3. Total files {len(uploaded_files)}"
        #     # st.toast('The number of files to import must be 3 (EO-FG-RPM).',  icon="⚠️")
        if len(lst_duoi_file_import) == 3:
            for file in uploaded_files:
                if Pattern.DOT.value in file.name:
                    duoifile = re.split(Pattern.DOT_PATTERN.value, file.name)[-1]
                else:
                    duoifile = None
                    
                if duoifile not in ValidateFile.LIST_DUOI_FILE_IMPORT.value:
                    return False, f"Invalid file type for {file.name}"
            return True, f"rtcis"
        elif len(lst_duoi_file_import) == 2:
            for extension in lst_duoi_file_import:
                if extension not in ValidateFile.LIST_DUOI_FILE_PRIME.value:
                    return False, f"Invalid file type for {extension}"
            return True, f"prime"
        else:
            return False, f"Unknown error import file"
    
    def import_file(self, uploaded_files: List) -> Tuple[bool, str, pd.DataFrame]:
        """Import inventory data from an uploaded file.
        
        Args:
            file_obj: File object from Streamlit file uploader
            
        Returns:
            Tuple containing:
                - Success flag (boolean)
                - Message (string)
        """
        #Check file upload
        is_valid, message = self._validate_file(uploaded_files)
        if not is_valid:
           return is_valid, f"{message}", None

        if message == "rtcis":
            #gọi inventory_model để xử lý và import file vào database
            success, number_rows_insert, df = self.inventory_model.save_inventory(uploaded_files)
            if success:
                if number_rows_insert == 0:
                    return True, f"You have inserted duplicate data", df
                else:
                    return True,  f"Successfully imported {number_rows_insert:,} inventory records", df
            else:
                return False, f"Failed to save inventory data to database", None
        elif message == "prime":
            df = self.inventory_model.process_inventory_prime(uploaded_files)
            return True,  f"Successfully imported inventory records", df
        
    def get_merge_data(self, date_time: Optional[List]=None) -> pd.DataFrame:
        """Lấy dataframe đã merge từ inventorymodel
        """
        try:
            df_merge = self.inventory_model.get_merge_data(date_time)
            return df_merge
        except Exception as e:
            logger.error(f"Get merge data error: {e}")
            raise