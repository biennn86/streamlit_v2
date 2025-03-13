import re 
import pandas as pd
import streamlit as st
from io import StringIO

class ReadFileInvModel:
    def __init__(self):
        self.data = None
        self.filename = None

    def cover_multifile_todict(self, uploaded_files):
        # Chuyển file import thành dict. Key chứa tên file, value chứa value data
        # Chỉ lấy 3 file cuối trong uploaded_files, khi user import nhiều file chưa clear cache được
        dict_files_data_soucre = {}
        get_3_last_file = uploaded_files[len(uploaded_files) - 3:]
        for file in get_3_last_file:
            if '.' in file.name:
                duoifile = re.split(r'\.', file.name)[-1]
            else:
                duoifile = None
                
            if duoifile in ['xlsx', 'xlsm', 'xls']:
                try:
                    data = pd.read_excel(file)
                    dict_files_data_soucre.update({file.name: data})
                except:
                    pass
            elif (duoifile in ['RPT', 'txt', 'TXT']) or (duoifile is None):
                data_txt = StringIO(file.getvalue().decode("utf-8"))
                dict_files_data_soucre.update({file.name: data_txt})
        return dict_files_data_soucre

    def validate_files(self, dict_data):
        regex_find_dot = re.compile(r'(\.)')
        regex_catfile = re.compile(r'(?<=Class:\s)(?:F|P)(?=\s+Item:)', re.MULTILINE)
        columns_eo = ['stt', 'barcode', 'lot#', 'po#', 'owner', 'gcas', 'description', 'supply_chain', 'type', 'status', 'created_by', 'created_date', 'wh_date', 'bin', 'assignment#', 'qty', 'remained_qty']
        IS_FILE_EO = False; IS_FILE_FG = False; IS_FILE_RPM = False
        #1: Check nội dung bên trong của từng file
        for key, value in dict_data.items():
            if '.' in key:
                match_dot = regex_find_dot.split(key)
                duoi_file = match_dot[-1]
                if duoi_file in ('xlsx', 'xlsm', 'xls'):
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
                    if cls_file == ['F']:
                        IS_FILE_FG = True
                    elif cls_file == ['P']:
                        IS_FILE_RPM = True
            else:
                cls_file = regex_catfile.findall(value.getvalue())
                if cls_file == ['F']:
                    IS_FILE_FG = True
                elif cls_file == ['P']:
                    IS_FILE_RPM = True

        if IS_FILE_EO and IS_FILE_FG and IS_FILE_RPM:
            return True
        else:
            return False
    
    def process_data(self, uploaded_files):
        list_df = []
        CAT_FG = 'F'
        dict_data = self.cover_multifile_todict(uploaded_files)
        isvalid = self.validate_files(dict_data)
        if isvalid:
            for key, value in dict_data.items():
                if '.' in key:
                    duoi_file = re.split(r'\.', key)[-1]
                else:
                    duoi_file = None

                if duoi_file in ('xlsx', 'xlsm', 'xls', 'csv'):
                    list_df.append(self.read_eo(value))
                else:
                    cat_file = re.search(r'(?<=Class:\s)(?:F|P)(?=\s+Item:)', value.getvalue(), re.MULTILINE).group()
                    if cat_file == CAT_FG:
                        date_time = re.search(r'(?:.+)(?=BinhDuong\sRTCIS)', value.getvalue(), re.MULTILINE).group().rstrip()
                    list_df.append(self.read_data_file(value))

        if list_df is not None:
            df_data_final = pd.concat(list_df, ignore_index=True)
            df_data_final.insert(0, 'date', date_time)
            return df_data_final
        else:
            return None
    
    def read_data_file(self, data):
        FG = 'F'; RPM = 'P'; LEN_RPM_LOST_VNL = 7; LEN_LINE_FINAL = 9
        #option 1: ^(?=\s*[0-9]{8})(.+)(?<=NONE) -> không lấy được dòng không có gcas và có batch bắt đầu bằng chữ
        #option 2:  ^(?=\s*).+(?<=NONE) -> lấy được tất cả các dòng thõa mãn điều kiện
        #option 3: ^(?:.+)(?<=NONE)(?:\b){0} -> lấy được tất cả các dòng thõa mãn điều kiện và tốc độ tính toán nhanh hơn
        pattern_getline_tonkho = re.compile(r'^(?:.+)(?<=NONE)(?:\b){0}', re.MULTILINE)
        pt_class_file = re.compile(r'(?<=Class:\s)(?:F|P)(?=\s+Item:)',  re.MULTILINE)
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
                data_line = line
                data_line = re.sub(r'(VN07)', "", data_line)
                data_line = re.sub(r'\s{2,}', ";", data_line)
                scile = re.search(r'(RL|QU|HD)', data_line).span()[0]
                data_line_left = data_line[:scile]
                data_line_right = data_line[scile:]
                data_line_left =  re.sub(r'\s{1,}', ";", data_line_left)
                data_line_right =  re.sub(r'\s{1,}', "", data_line_right)
                data_line_final = data_line_left + data_line_right
                data_line_final = data_line_final.split(";")
            
                if (cls_match == FG):
                    data_line_final.insert(2, 'VNL_FG')
                    data_line_final.append('FG')

                if (cls_match == RPM):
                    if (len(data_line_final) == LEN_RPM_LOST_VNL):
                        data_line_final.insert(2, 'RPM_LOST_VNL')
                        data_line_final.append('RPM')
                    else:
                        data_line_final.append('RPM')

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
            except:
                print('Lỗi đọc file txt: f(read_data_file)')
                pass
    
        df_data = self.create_df_tonkho_from_list(list_data)
        return df_data

    def create_df_tonkho_from_list(self, data):
        columns_inv = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note_inv', 'cat_inv']
        df_data = pd.DataFrame(data, columns = columns_inv)
        df_data = df_data.astype('string')
        return df_data
    
    def read_eo(self, df_eouploaded):
        df_eo = df_eouploaded.copy()
        # df_eo = pd.read_excel(link_file)
        columns_eo = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note_inv' , 'cat_inv']
        df_eo = df_eo[['GCAS', 'Lot#', 'Barcode', 'Qty', 'Bin', 'Type']]
        df_eo['Bin'] = df_eo['Bin'].apply(lambda x: re.sub(r'[ ]', '', x.upper()))
        df_eo.insert(3, 'status', 'RL')
        df_eo.insert(5, 'pallet', 1)
        df_eo.insert(8, 'cat_inv', 'EO')
        df_eo.columns = columns_eo
        df_eo = df_eo.astype('string')
        return df_eo
    

        