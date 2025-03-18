import streamlit as st
from views.View import View
from utils.constants import PAGE_CONFIG
from views.UploadFileView import UploadFileView
from views.DashBoardView import DashBoardView

class Main:
    def __init__(self):
        pass

    def init_page_config(self):
        st.set_page_config(
        page_title=PAGE_CONFIG["page_title"],
        page_icon=PAGE_CONFIG["page_icon"],
        layout=PAGE_CONFIG["layout"],
        initial_sidebar_state=PAGE_CONFIG["initial_sidebar_state"],
        menu_items=PAGE_CONFIG["menu_items"]
        )
        
    def showmenu(self):
        View().import_files_inventory()
        View().create_location()
        View().update_masterdata()
        View().tab_dashboard()

    def import_file(self):
        upload_files = View().import_files_inventory()


if __name__ == "__main__":
    Main().init_page_config()
    upload_view = UploadFileView()
    upload_view.render_upload_section()
    db = DashBoardView().showlocation()
    print(db)
    
