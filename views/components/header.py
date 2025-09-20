import streamlit as st
from datetime import datetime

def render_header(title="Dashboard", show_time=True):
    '''Render header của ứng dụng'''
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header(title)

    with col2:
        if show_time:
            current_time = datetime.now().strftime("%H:%M:%S")
            st.header(f"Thời gian: {current_time}")