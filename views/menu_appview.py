import streamlit as st

class MenuApp:
    '''
    Hiển thị các menubar như import inventory, create location, update masterdata trên trình duyệt.
    '''
    def reset_session_on_file_upload(self):
        st.session_state.uploaded_files = None

    def import_files_inventory(self):
        with st.sidebar:
            with st.expander('Import Files Inventory'):
                # st.session_state.uploaded_files
                return st.file_uploader('Choose Files Inventory FG-RPM-EO', accept_multiple_files=True, on_change=self.reset_session_on_file_upload)
    
    def create_location(self):
        with st.sidebar:
            with st.expander('Create Location'):
                return st.button('Create Location')

    def update_masterdata(self):
        with st.sidebar:
            with st.expander('Update Master Data'):
                return st.file_uploader('Choose File Master Data', accept_multiple_files=False)