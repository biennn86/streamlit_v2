import streamlit as st

class MenuApp:
    def import_files_inventory(self):
        with st.sidebar:
            with st.expander('Import Files Inventory'):
                # st.session_state.uploaded_files
                uploaded_files = st.file_uploader('Choose Files Inventory FG-RPM-EO', accept_multiple_files=True)
                return uploaded_files
    
    def create_location(self):
        with st.sidebar:
            with st.expander('Create Location'):
                st.button('Create Location')

    def update_masterdata(self):
        with st.sidebar:
            with st.expander('Update Master Data'):
                uploaded_file_mtdt = st.file_uploader('Choose File Master Data', accept_multiple_files=False)