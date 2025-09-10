import re
import pandas as pd
from models.table.tablename_database import TableNameMasterdata

class MasterdataModel:
    def process_file_masterdata(self, linkfile_masterdata):
        df_master_data = pd.read_excel(linkfile_masterdata)
        obj_master_data = TableNameMasterdata()
        # delete 2 rows last
        last_row = len(df_master_data)
        df_master_data = df_master_data.drop([last_row - 2, last_row - 1])
        #process
        df_master_data.columns = [re.sub(r'[ -]', "_", string).lower().strip() for string in df_master_data.columns]
        df_master_data['cat'] = df_master_data['cat'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['type1'] = df_master_data['type1'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['type2'] = df_master_data['type2'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
        df_master_data['source'] = df_master_data['source'].apply(lambda string: str(string).lower().strip())
        #insert to database
        obj_master_data.insert_dataframe(df_master_data)