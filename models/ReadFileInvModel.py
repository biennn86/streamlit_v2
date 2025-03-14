import re 
import pandas as pd
import streamlit as st
from utils.constants import ValidateFile, Pattern, Columns, VNL_CAT
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

    def validate_files(self, dict_data):
        regex_find_dot = re.compile(Pattern.DOT_PATTERN.value)
        regex_catfile = re.compile(Pattern.CATEGORY_FILE.value, re.MULTILINE)
        columns_eo = Columns.COLUMNS_FILE_EO.value
        IS_FILE_EO = False; IS_FILE_FG = False; IS_FILE_RPM = False
        #1: Check nội dung bên trong của từng file
        for key, value in dict_data.items():
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
    
    def process_data(self, uploaded_files):
        list_df = []
        CAT_FG = ValidateFile.CATEGORY_FG.value
        dict_data = self.cover_multifile_todict(uploaded_files)
        isvalid = self.validate_files(dict_data)
        if isvalid:
            for key, value in dict_data.items():
                if Pattern.DOT.value in key:
                    duoi_file = re.split(Pattern.DOT_PATTERN.value, key)[-1]
                else:
                    duoi_file = None

                if duoi_file in ValidateFile.LIST_DUOI_FILE_EO.value:
                    list_df.append(self.read_eo(value))
                else:
                    cat_file = re.search(Pattern.CATEGORY_FILE.value, value.getvalue(), re.MULTILINE).group()
                    if cat_file in CAT_FG:
                        date_time = re.search(Pattern.GET_DATETIME.value, value.getvalue(), re.MULTILINE).group().rstrip()
                    list_df.append(self.read_data_file(value))

        if list_df is not None:
            df_data_final = pd.concat(list_df, ignore_index=True)
            df_data_final.insert(0, 'date', date_time)
            return df_data_final
        else:
            return None
    
    def read_data_file(self, data):
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
                data_line = re.sub(Pattern.VN07.value, "", line)
                data_line = re.sub(Pattern.TWO_SPACE.value, ";", line)
                scile = re.search(Pattern.STATUS.value, line).span()[0]
                data_line_left = data_line[:scile]
                data_line_right = data_line[scile:]
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
    
        df_data = self.create_df_tonkho_from_list(list_data)
        return df_data

    def create_df_tonkho_from_list(self, data):
        columns_inv = Columns.COLUMNS_INV.value
        df_data = pd.DataFrame(data, columns = columns_inv)
        df_data = df_data.astype('string')
        return df_data
    
    def read_eo(self, df_eouploaded):
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
    

        