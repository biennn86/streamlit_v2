import sys
import re
import tk as tk
from tk import filedialog
import pandas as pd
from control.tonkho import Inventory

# def create_data_rtcis():
#     links_file = get_path_import_file()
#     if len(links_file) == 0:
#         exit()
#     elif len(links_file) < 3:
#         print('Chưa chọn đủ file!')
#         exit()
#     elif len(links_file) > 3:
#         print('Chỉ được chọn 1 lúc 3 file.')
#         exit()

#     list_df = []
#     for link in links_file:
#         find_dot = link.find(".")
#         if find_dot != -1:
#             duoifile = link[find_dot + 1:len(link)]
#             list_df.append(read_eo(link))
#         else:
#             data = read_file_txt(link)
#             if data[3].find('Class: F') != -1:
#                 date_time = data[0][0:20]

#             list_df.append(read_data_file(data))
#     df_data_final = pd.concat(list_df, ignore_index=True)
#     df_data_final.insert(0, 'date', date_time)
#     return df_data_final

def create_data_rtcis(dict_data):
    list_df = []
    CAT_FG = 'F'
    for key, value in dict_data.items():
        if '.' in key:
            duoi_file = re.split(r'\.', key)[-1]
        else:
            duoi_file = None

        if duoi_file in ('xlsx', 'xlsm', 'xls', 'csv'):
            list_df.append(read_eo(value))
        else:
            cat_file = re.search(r'(?<=Class:\s)(?:F|P)(?=\s+Item:)', value.getvalue(), re.MULTILINE).group()
            if cat_file == CAT_FG:
                date_time = re.search(r'(?:.+)(?=BinhDuong\sRTCIS)', value.getvalue(), re.MULTILINE).group().rstrip()
            list_df.append(read_data_file(value))
            # value.seek(0)
            # for _ in range(4):
            #     row = value.readline()
            # if row.find('Class: F') != -1:
            #     cat_file = 'FG'
            #     value.seek(0)
            #     date_time = value.readline(20).rstrip()
    if list_df is not None:
        df_data_final = pd.concat(list_df, ignore_index=True)
        df_data_final.insert(0, 'date', date_time)
        return df_data_final
    else:
        return None
    



def read_data_file(data):
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
    
    df_data = create_df_tonkho_from_list(list_data)
    return df_data

def read_file_txt(link_file):
    with open(link_file, 'r') as file:
        data_readed = file.readlines()
    return data_readed

def get_path_import_file():
    file_type = [
        ('All File', '*.*'),
        ('CSV File', "*.csv"),
        ('Excel File', ['*.xlsx', '*.xlsm'])   
    ]
    file_path = filedialog.askopenfilename(title='Chose File', multiple=True, filetypes=file_type)
    root = tk.Tk()
    root.withdraw()
    return file_path

def create_df_tonkho_from_list(data):
    columns_inv = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note_inv', 'cat_inv']
    #Cách 1
    df_data = pd.DataFrame(data, columns = columns_inv)
    return df_data
    #Cách 2
    # list_series = []
    # for line in data:
    #     line = tuple(line)
    #     data_series = pd.Series(line, title)
    #     list_series.append(data_series)
    # df_data = pd.concat(list_series, axis=1).T.reset_index(drop=True)

# def read_eo(link_file):
#     df_eo = pd.read_excel(link_file)
#     columns = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note' , 'category_inv']
#     df_eo = df_eo[['GCAS', 'Lot#', 'Barcode', 'Qty', 'Bin', 'Type']]
#     df_eo['Bin'] = df_eo['Bin'].apply(lambda x: re.sub(r'[ ]', '', x.upper()))
#     df_eo.insert(3, 'status', 'RL')
#     df_eo.insert(5, 'pallet', 1)
#     df_eo.insert(8, 'category_inv', 'EO')
#     df_eo.columns = columns
#     return df_eo

def read_eo(df_eouploaded):
    df_eo = df_eouploaded.copy()
    # df_eo = pd.read_excel(link_file)
    columns_eo = ['gcas', 'batch', 'vnl', 'status', 'qty', 'pallet', 'location', 'note_inv' , 'cat_inv']
    df_eo = df_eo[['GCAS', 'Lot#', 'Barcode', 'Qty', 'Bin', 'Type']]
    df_eo['Bin'] = df_eo['Bin'].apply(lambda x: re.sub(r'[ ]', '', x.upper()))
    df_eo.insert(3, 'status', 'RL')
    df_eo.insert(5, 'pallet', 1)
    df_eo.insert(8, 'cat_inv', 'EO')
    df_eo.columns = columns_eo
    return df_eo

def import_tonkho_to_db(df_tonkho):
    Inventory().insert_data_from_df(df_tonkho, 'append')

