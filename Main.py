import streamlit as st
from views.Tabs import Tabs
from views.menu_appview import MenuApp
from utils.constants import PAGE_CONFIG
from views.UploadFileView import UploadFileView
from views.MergeDataView import MergeDataView

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
        MenuApp().import_files_inventory()
        MenuApp().create_location()
        MenuApp().update_masterdata()
        Tabs().tab_dashboard()

    def import_file(self):
        upload_files = MenuApp().import_files_inventory()


if __name__ == "__main__":
    Main().init_page_config()
    upload_view = UploadFileView()
    df_inv = upload_view.render_upload_section()
    db = MergeDataView().render_mergedata(df_inv)
    
