import streamlit as st
from core.app_manager import AppManager
from config.settings import AppConfig

def handle_new_import_inv_btb():
    #Thay đổi trạng thái file upload từ mặc định False thành True khi có upload file mới
    AppManager().state.set(AppConfig.StateKeys.FILE_UPLOADER_INV_BTB, True)
    # print(f"Status file_uploader sau khi onchange: {AppManager().state.get(AppConfig.StateKeys.FILE_UPLOADER, 'Bien')}")

    #Xử lý khi import file mới
    current_key = f"file_uploader_btb_{AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_INV_BTB)}"
    # Lấy dữ liệu file người dùng vừa chọn từ widget hiện tại
    new_files = AppManager().state.get(current_key, [])
    if new_files:
        # Lấy danh sách tên file hiện tại vừa import
        # current_file_names = [f.name for f in new_files]
        #Nếu danh sách file này KHÁC hoàn toàn với danh sách file của lần import trước
        # last_files = AppManager().state.get(AppConfig.StateKeys.LAST_PROCESSED_FILES, [])
        # if current_file_names != last_files: #AppConfig.StateKeys.LAST_PROCESSED_FILES:
        # Cập nhật danh sách lịch sử mới
        #AppManager().state.set(AppConfig.StateKeys.LAST_PROCESSED_FILES, current_file_names)
        # Cất file vào biến lưu trữ độc lập
        AppManager().state.set(AppConfig.StateKeys.CURRENT_FILE_INV_BTB, new_files)
        # Tăng ID ngay tại đây để widget tự động đổi sang key mới ở dòng dưới
        AppManager().state.set(AppConfig.StateKeys.UPLOAD_ID_INV_BTB, AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_INV_BTB, 0) + 1)

def handle_new_import_demand():
    #Thay đổi trạng thái file upload từ mặc định False thành True khi có upload file mới
    AppManager().state.set(AppConfig.StateKeys.FILE_UPLOADER_DEMAND, True)
    # print(f"Status file_uploader sau khi onchange: {AppManager().state.get(AppConfig.StateKeys.FILE_UPLOADER, 'Bien')}")

    #Xử lý khi import file mới
    current_key = f"file_uploader_demand_{AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_DEMAND)}"
    # Lấy dữ liệu file người dùng vừa chọn từ widget hiện tại
    new_files = AppManager().state.get(current_key, [])
    if new_files:
        # Lấy danh sách tên file hiện tại vừa import
        # current_file_names = [f.name for f in new_files]
        #Nếu danh sách file này KHÁC hoàn toàn với danh sách file của lần import trước
        # last_files = AppManager().state.get(AppConfig.StateKeys.LAST_PROCESSED_FILES, [])
        # if current_file_names != last_files: #AppConfig.StateKeys.LAST_PROCESSED_FILES:
        # Cập nhật danh sách lịch sử mới
        #AppManager().state.set(AppConfig.StateKeys.LAST_PROCESSED_FILES, current_file_names)
        # Cất file vào biến lưu trữ độc lập
        AppManager().state.set(AppConfig.StateKeys.CURRENT_FILE_DEMAND, new_files)
        # Tăng ID ngay tại đây để widget tự động đổi sang key mới ở dòng dưới
        AppManager().state.set(AppConfig.StateKeys.UPLOAD_ID_DEMAND, AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_DEMAND, 0) + 1)

def import_inv_prime_csv_btb():
    # Tạo key động cho lần import hiện tại
    current_uploader_key = f"file_uploader_btb_{AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_INV_BTB)}"
    with st.sidebar:
        with st.expander('Import File Inventory'):
            st.file_uploader('Choose File Inventory Prime CSV',
                                accept_multiple_files=False,
                                key=current_uploader_key,
                                type=["csv"],
                                on_change=handle_new_import_inv_btb)
    if AppManager().state.get(AppConfig.StateKeys.CURRENT_FILE_INV_BTB, []):
        files_to_process = AppManager().state.get(AppConfig.StateKeys.CURRENT_FILE_INV_BTB, [])
        return files_to_process
    
def import_demand_excel_btb():
    # Tạo key động cho lần import hiện tại
    current_uploader_key = f"file_uploader_demand_{AppManager().state.get(AppConfig.StateKeys.UPLOAD_ID_DEMAND)}"
    with st.sidebar:
        with st.expander('Import File Demand'):
            st.file_uploader('Choose File Demand Excel',
                                accept_multiple_files=False,
                                key=current_uploader_key,
                                type=["xlsx", "xlsm"],
                                on_change=handle_new_import_demand)
    if AppManager().state.get(AppConfig.StateKeys.CURRENT_FILE_DEMAND, []):
        files_to_process = AppManager().state.get(AppConfig.StateKeys.CURRENT_FILE_DEMAND, [])
        return files_to_process

def sidebar_button_btb():
    with st.sidebar:
        with st.expander('Run BinToBin'):
            return st.button('Run BinToBin')

