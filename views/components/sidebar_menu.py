import streamlit as st
from core.app_manager import AppManager
from config.settings import AppConfig

def handle_new_import():
    #Thay đổi trạng thái file upload từ mặc định False thành True khi có upload file mới
    AppManager().state.set(AppConfig.StateKeys.FILE_UPLOADER, True)
    # print(f"Status file_uploader sau khi onchange: {AppManager().state.get(AppConfig.StateKeys.FILE_UPLOADER, 'Bien')}")

    #Xử lý khi import file mới
    current_key = f"file_uploader_{AppManager().state.get(AppConfig.StateKeys.UPLOADER_ID)}"
    # Lấy dữ liệu file người dùng vừa chọn từ widget hiện tại
    new_files = AppManager().state.get(current_key, [])
    if new_files:
        # Lấy danh sách tên file hiện tại vừa import
        current_file_names = [f.name for f in new_files]
        #Nếu danh sách file này KHÁC hoàn toàn với danh sách file của lần import trước
        if current_file_names != AppConfig.StateKeys.LAST_PROCESSED_FILES:
            # Cập nhật danh sách lịch sử mới
            AppManager().state.set(AppConfig.StateKeys.LAST_PROCESSED_FILES, current_file_names)
            # Cất file vào biến lưu trữ độc lập
            AppManager().state.set(AppConfig.StateKeys.CURRENT_FILES, new_files)
            # Tăng ID ngay tại đây để widget tự động đổi sang key mới ở dòng dưới
            AppManager().state.set(AppConfig.StateKeys.UPLOADER_ID, AppManager().state.get(AppConfig.StateKeys.UPLOADER_ID, 0) + 1)
    

def sidebar_import_files_inventory():
    # Tạo key động cho lần import hiện tại
    current_uploader_key = f"file_uploader_{AppManager().state.get(AppConfig.StateKeys.UPLOADER_ID)}"
    with st.sidebar:
        with st.expander('Import Files Inventory'):
            st.file_uploader('Choose Files Inventory FG-RPM-EO',
                                    accept_multiple_files=True,
                                    key=current_uploader_key,
                                    on_change=handle_new_import)
    if AppManager().state.get(AppConfig.StateKeys.CURRENT_FILES, []):
        files_to_process = AppManager().state.get(AppConfig.StateKeys.CURRENT_FILES, [])
        return files_to_process

def sidebar_create_location():
    with st.sidebar:
        with st.expander('Create Location'):
            return st.button('Create Location')

def sidebar_update_masterdata():
    with st.sidebar:
        with st.expander('Update Master Data'):
            return st.file_uploader('Choose File Master Data', accept_multiple_files=False)