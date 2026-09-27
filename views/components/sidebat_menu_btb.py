import streamlit as st

def import_inv_prime_csv_btb():
    with st.sidebar:
        with st.expander('Import Files Inventory'):
            return st.file_uploader('Choose Files Inventory Prime CSV',
                                    accept_multiple_files=False,
                                    key="inventory_uploader",
                                    type=["csv"],
                                    on_change=None)
def import_demand_excel_btb():
    with st.sidebar:
        with st.expander('Import Files Demand'):
            return st.file_uploader('Choose Files Demand Excel',
                                    accept_multiple_files=False,
                                    key="demand_uploader",
                                    type=["xlsx", "xlsm"],
                                    on_change=None)

def sidebar_button_btb():
    with st.sidebar:
        with st.expander('Run BinToBin'):
            return st.button('Run BinToBin')

