import streamlit as st
from core.app_manager import AppManager
from config.settings import AppConfig

def change_status_file_uploader():
    return AppManager().state.set(AppConfig.StateKeys.FILE_UPLOADER, True)

def sidebar_import_files_inventory():
    with st.sidebar:
        with st.expander('Import Files Inventory'):
            # st.session_state.uploaded_files
            return st.file_uploader('Choose Files Inventory FG-RPM-EO', accept_multiple_files=True, on_change=change_status_file_uploader)

def sidebar_create_location():
    with st.sidebar:
        with st.expander('Create Location'):
            return st.button('Create Location')

def sidebar_update_masterdata():
    with st.sidebar:
        with st.expander('Update Master Data'):
            return st.file_uploader('Choose File Master Data', accept_multiple_files=False)