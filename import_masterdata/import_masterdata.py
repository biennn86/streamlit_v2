import re
import pandas as pd
from control.masterdata import MasterData


def import_mtdt(linkfile_masterdata):
    df_master_data = pd.read_excel(linkfile_masterdata)
    obj_master_data = MasterData()
    df_master_data.columns = [re.sub(r'[ -]', "_", string).lower().strip() for string in df_master_data.columns]
    df_master_data['cat'] = df_master_data['cat'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['type1'] = df_master_data['type1'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['type2'] = df_master_data['type2'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['source'] = df_master_data['source'].apply(lambda string: str(string).lower().strip())
    obj_master_data.insert_data_from_df(df_master_data, 'append')