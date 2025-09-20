import datetime
import pandas as pd
from readtrans.read_trans_rtcis import *
from readtrans.analysis_data import *
from controllers.datatrans import DataTrans
from controllers.location import Location
from controllers.masterdata import MasterData
from controllers.data_after_analy import DataAnalys
from extend.any_extend import *

from create_location.create_loc import *

def read_file_trans_tosql():
    starttime = datetime.now()
    path_open_csv = get_path_import_file()

    obj_transaction = ReadDatatrans(path_open_csv)
    obj_datatrans_to_db = DataTrans()
    lst_transaction = obj_transaction.get_data_trans_from_excel()
    df_transaction = obj_transaction.create_df_from_list(lst_transaction)
    obj_datatrans_to_db.insert_data_from_df(df_transaction, 'replace')

    endtime = datetime.now()
    time_diference = obj_transaction.time_loading(starttime, endtime)
    print("Đã chạy xong, thời gian chạy: {}".format(time_diference))

# read_file_trans_tosql()

def read_excel_loc_user_tosql():
    '''
    Đã có file tạo location mới. Không xài import masterloc từ file excel nữa
    '''
    path_open_locuser = get_path_import_file()
    # sheetname create df loc, user
    sheet_name_loc = "location"
    sheet_name_user  = "masteruser"
    col_loc = ['location', 'type_loc', 'category_loc', 'level_loc', 'wh_name', 'stacklimit', 'footprint']
    col_user = ['user', 'group_user', 'position', 'name', 'mail', 'phone', 'email_pg']
    #khởi tạo obj Location, User để lấy tên table trong db
    obj_location_to_db = Location()
    obj_user_to_db = User()
    #tạo obj Readcsv... để lấy phương thức read_excel_to_df
    obj_loc_user = ReadCsvExcelToDataframe(path_open_locuser)
    df_loc = obj_loc_user.read_excel_to_dataframe(sheet_name_loc)
    df_user = obj_loc_user.read_excel_to_dataframe(sheet_name_user)
    df_loc.columns = col_loc
    df_user.columns = col_user
    #đưa df vào db
    obj_location_to_db.insert_data_from_df(df_loc, 'replace')
    obj_user_to_db.insert_data_from_df(df_user, 'replace')
# read_excel_loc_user_tosql()

def read_excel_master_data_tosql():
    sheet_name_masterdata = 'Export'
    path_master_data = get_path_import_file()
    obj_master_data = MasterData()
    obj_data = ReadCsvExcelToDataframe(path_master_data)
    df_master_data = obj_data.read_excel_to_dataframe(sheet_name_masterdata)
    df_master_data.columns = [re.sub(r'[ -]', "_", string).lower().strip() for string in df_master_data.columns]
    df_master_data['cat'] = df_master_data['cat'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['type1'] = df_master_data['type1'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['type2'] = df_master_data['type2'].apply(lambda string: re.sub(r'[ ]', "_", string).lower().strip())
    df_master_data['source'] = df_master_data['source'].apply(lambda string: str(string).lower().strip())
    obj_master_data.insert_data_from_df(df_master_data, 'append')
# read_excel_master_data_tosql()

def analysis_data_to_sql():
    starttime = datetime.now()
    #khởi tạo đối tượng phân tích và get data from database
    obj_analysis_data = AnalysProductivity()
    obj_data_after_analys = DataAnalys()
    df_final = obj_analysis_data.process_df()
   
    
    #đưa df vừa tổng hợp được vào database
    obj_data_after_analys.insert_data_from_df(df_final, 'replace')
    df_a = obj_data_after_analys.get_df_from_db()
    # df_a['date_shift'] = pd.to_datetime(df_a['date_shift'])
    # df_a['time_in'] = pd.to_datetime(df_a['time_in']) #, format='%H:%M:%S.%f'
    # df_a['time_out'] = pd.to_datetime(df_a['time_out'])
    print(df_a)

    endtime = datetime.now()
    time_diference = time_loading(starttime, endtime)
    print("Đã chạy xong, thời gian chạy: {}".format(time_diference))

# analysis_data_to_sql()







def main_cls_read_data_from_excel():
	starttime = datetime.now()

	path = 'file_source/get_transaction_rtcis_070424 GuiMinh.xlsm'
	name_sh = 'DataFormRTCIS'
	# path = 'file_source/data_rtcis_test.xlsx'
	# name_sh = 'Sheet1'
	data = ReadDatatrans(path, name_sh)
	result = data.get_data_from_dataframe()
	print("Tổng Dòng Tổng Hợp Được: {}".format(len(result)))
	data.write_data_to_txt()

	df_tonghop = data.create_df_from_list(result)
	data.write_data_to_csv()
	# print(df_tonghop.head(20))
	
	endtime = datetime.now()
	time_diference = data.time_loading(starttime, endtime)
	print("Đã chạy xong, thời gian chạy: {}".format(time_diference))

	#------------------------------------------------------------------------------
	

# main_cls_read_data_from_excel()
