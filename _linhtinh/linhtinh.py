import tkinter as tk
from tkinter import filedialog

def import_file():
    f_types = [('All Files', '*.*'), 
            ('Python Files', '*.py'),
            ('Text Document', '*.txt'),
            ('CSV files',"*.csv"),
            ('Excel File', ['*.xlsx', '*.xlsm'])]
    file_path = filedialog.askopenfilename(title="Chọn File Để Mở", multiple=False, filetypes=f_types)
    print("Đường dẫn tệp đã chọn:", file_path)
    # Xử lý tệp đã chọn ở đây

root = tk.Tk()
root.withdraw() # Ẩn cửa sổ chính của tkinter

import_file()
