import logging
import re
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT
from models.inventory import InventoryModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        if (len(uploaded_files) == 0):
            return False, f"No file uploaded"
        elif len(uploaded_files) % 3 != 0:
            return False, f"The number of imported files must be divisible by 3. Total files {len(uploaded_files)}"
            # st.toast('The number of files to import must be 3 (EO-FG-RPM).',  icon="⚠️")
        for file in uploaded_files:
            if Pattern.DOT.value in file.name:
                duoifile = re.split(Pattern.DOT_PATTERN.value, file.name)[-1]
            else:
                duoifile = None
                
            if duoifile not in ValidateFile.LIST_DUOI_FILE_IMPORT.value:
                return False, f"Invalid file type for {file.name}"
        return True, f"Valid file"
    
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
        
        #gọi inventory_model để xử lý và import file vào database
        success, df = self.inventory_model.save_inventory(uploaded_files)
        if success:
            return True,  f"Successfully imported {len(df):,} inventory records", df
        else:
            return False, f"Failed to save inventory data to database", None
        
    def get_merge_data(self, date_time: Optional[List]=None) -> pd.DataFrame:
        """Lấy dataframe đã merge từ inventorymodel
        """
        try:
            df_merge = self.inventory_model.get_merge_data(date_time)
            return df_merge
        except Exception as e:
            logger.error(f"Get merge data error: {e}")
            raise