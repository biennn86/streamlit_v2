import streamlit as st
from views.MenuApp import MenuApp
from views.Tabs import Tabs
from controllers.ReadFileInvController import ReadFileInvController

class UploadFileView(MenuApp):
    '''
    Kế thừa MenuApp để hiển thị các menu trên trình duyệt.
    Nhận kết quả xử lý của controller.
    '''
    def __init__(self):
        self.controller = ReadFileInvController()
    
    def render_upload_section(self):
        uploaded_files = MenuApp().import_files_inventory()
        results  = self.controller.process_files(uploaded_files)
        # Hiển thị kết quả
        if results['success']:
            for success in results['success']:
                st.toast(success, icon="ℹ️")
            # Hiển thị dữ liệu đã gộp
            # st.dataframe(results['combined_data'])
            # Tabs().tab_dashboard(results['combined_data'])
            return results['combined_data']
        # Hiển thị lỗi nếu có
        if results['errors']:
            for error in results['errors']:
                st.toast(error['error'], icon="⚠️")