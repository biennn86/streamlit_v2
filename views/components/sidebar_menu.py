import streamlit as st
from core.app_manager import AppManager
from config.settings import AppConfig

def on_file_change():
    AppManager().state.set(AppConfig.StateKeys.FILE_UPLOADER, True)
    # print(f"Status file_uploader sau khi onchange: {AppManager().state.get(AppConfig.StateKeys.FILE_UPLOADER, 'Bien')}")
    

def sidebar_import_files_inventory():
    with st.sidebar:
        with st.expander('Import Files Inventory'):
            return st.file_uploader('Choose Files Inventory FG-RPM-EO', accept_multiple_files=True, on_change=on_file_change)

def sidebar_create_location():
    with st.sidebar:
        with st.expander('Create Location'):
            return st.button('Create Location')

def sidebar_update_masterdata():
    with st.sidebar:
        with st.expander('Update Master Data'):
            return st.file_uploader('Choose File Master Data', accept_multiple_files=False)