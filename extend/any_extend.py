import tkinter as tk
from tkinter import filedialog

def get_path_import_file():
    file_type = [
        ('CSV File', "*.csv"),
        ('Excel File', ['*.xlsx', '*.xlsm'])
    ]
    file_path = filedialog.askopenfilename(title='Chose File', multiple=False, filetypes=file_type)
    root = tk.Tk()
    root.withdraw()
    return file_path

def time_loading(start, end):
    time_difference = end - start
    total_seconds = time_difference.total_seconds()
    minutes  = int(total_seconds // 60)
    seconds = round(int(total_seconds % 60),0)
    time_load = str(f'{minutes:02d}') + ":" + str(f'{seconds:02d}')
    return time_load