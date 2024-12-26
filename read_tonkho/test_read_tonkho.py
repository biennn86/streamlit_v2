import re
import pandas as pd

class Readtextfile:
    def __init__(self, item, batch, vnl, status, qty, uls, location, note):
        self.item = item
        self.batch = batch
        self.vnl = vnl
        self.status = status
        self.qty = qty
        self.uls = uls
        self.location = location
        self.note = note

    def cover_object_to_string(self):
        TEXT_APPEND = ";"
        data_writer = (self.item + TEXT_APPEND + self.batch + TEXT_APPEND + self.vnl + TEXT_APPEND + 
                       self.status + TEXT_APPEND + self.qty + TEXT_APPEND + self.uls + TEXT_APPEND + 
                       self.location + TEXT_APPEND + self.note)
        
        return data_writer


def read_row_txt(data_row):
    def get_row(row_text):
        if row_text.find("NONE") != -1:
            return True
        return False

    def process_row(row_text):
        # Loại bỏ các ký tự xuống dòng, ký tự thừa phía sau nhưu OUT OF SEVEIR, và bỏ ký tự VN07 ở dòng đầu tiên
        row_text = row_text.rstrip()[:84].replace(" VN07 ", "")
        row_text = row_text.replace("  ",",")
        # Cắt đôi row để xử lý space, vì có trong file có những vị trí có spcae
        number_clear = int(len(row_text)*0.6)
        row_text_left = row_text[:number_clear]
        row_text_right = row_text[number_clear:]

        row_text_left = row_text_left.replace(" ",",")
        row_text_right = row_text_right.replace(" ","")
        row_text = row_text_left + row_text_right
        row_text = clear_comma_to_list(row_text)

        return row_text

    def clear_comma_to_list(row_text):
        while row_text.find(",,") != -1:
            row_text = row_text.replace(",,",",")

        row_text = row_text.split(",")
        return row_text
    
    # Core hàm read_row_txt
    if get_row(data_row):
        data_row = process_row(data_row)
        # Line hàng FG không có VNL, phải thêm vào để đồng nhất với file RPM
        if len(data_row) == 7:
            data_row.insert(2, "Insert_More")

        item, batch, vnl, status, qty, uls, location, note = data_row
        data = Readtextfile(item, batch, vnl, status, qty, uls, location, note)

        return data
    

def read_rows_txt():
    with open('RPM_20231213_1235.txt', 'r') as file:
        data_readed = file.readlines()
    data = []
    for data_row in data_readed:
        data_row_append = read_row_txt(data_row)
        if data_row_append != None:
            if len(data_row_append.item) == 0:
                data_row_append.item = data[-1].item
                data.append(data_row_append)
            else:
                data.append(data_row_append)
    print("Successfully read data from txt")
    return data

def write_data_from_txt(data):
    data_write = []
    with open('data_result.txt', 'w') as file:
        for line in data:
            line_write = line.cover_object_to_string()
            data_write.append(line_write + '\n')
            # file.write(line_write+'\n')        
         
        file.writelines(data_write)
    print("Successfully write data to txt")

def write_data_to_excel():
    with open('data_result.txt', 'r') as file:
        data = pd.read_csv(file, sep=";")

    with pd.ExcelWriter('output.xlsx', engine='xlsxwriter', mode='w') as writer:
        data.to_excel(writer, index=False, header=True, startrow=0)

        # Lấy đối tượng workbook từ writer
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        worksheet.set_column('A:H', 12)

    print("Successfully write data to excel")

def main():
    data = read_rows_txt()
    write_data_from_txt(data)
    write_data_to_excel()
main()