import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from views.components.sidebat_menu_btb import *
from models.inventory_model import InventoryModel
from models.bintobin_model import BintobinModel
from controllers.bintobin_controller import BintobinController

class BintobinView:
    def __init__(self):
        inventory_model = InventoryModel()
        bintobin_model = BintobinModel(inventory_model)
        self.bintobin_controller = BintobinController(bintobin_model)

    def import_inv_prime_csv(self):
        link_ton_kho_csv = import_inv_prime_csv_btb()
        if link_ton_kho_csv:
            self.file_ton_kho_csv = self.bintobin_controller.import_file_tonkho_prime(link_ton_kho_csv)

    def import_file_demand(self):
        link_file_demand = import_demand_excel_btb()
        if link_file_demand:
            self.file_demand = self.bintobin_controller.import_file_demand(link_file_demand)

    def run_bintobin(self):
        button_btb = sidebar_button_btb()
        if button_btb:
            self.df_btb = self.bintobin_controller.run_bintobin(self.file_ton_kho_csv, self.file_demand)

    def render_page_btb(self):
        self.import_inv_prime_csv()
        self.import_file_demand()
        self.run_bintobin()

        #Create layout bin to bin
        cont_bintobin = st.container(border=StatusBorder.BORDER.value)
        title_btb_rack = cont_bintobin.container(border=StatusBorder.BORDER.value)
        btb_rack = cont_bintobin.container(border=StatusBorder.BORDER.value)

        title_btb_ww = cont_bintobin.container(border=StatusBorder.BORDER.value)
        btb_ww = cont_bintobin.container(border=StatusBorder.BORDER.value)

        #Lọc datafram rack và ww
        try:
            if isinstance(self.df_btb, pd.DataFrame):
                mask = pd.Series(True, self.df_btb.index)
                mask_is_rack = mask & self.df_btb['location_system_type'].isin(["PF"])
                mask_is_ww = mask & self.df_btb['location_system_type'].isin(["WW"])

                df_btb_rack = self.df_btb[mask_is_rack]
                df_btb_rack = df_btb_rack.sort_values(by=["location"])
                num_bin_rack = len(df_btb_rack)

                df_btb_ww = self.df_btb[mask_is_ww]
                df_btb_ww = df_btb_ww.sort_values(by=["location"])
                num_bin_ww = len(df_btb_ww)

            else:
                num_bin_rack = 0
                num_bin_ww = 0
        except:
            df_btb_rack = pd.DataFrame()
            df_btb_ww = pd.DataFrame()
            num_bin_rack = 0
            num_bin_ww = 0

        with title_btb_rack:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">LIST BIN TO BIN IN RACK {num_bin_rack}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

        with btb_rack:
            st.html(f"<span class='df_btb'</span>")
            st.dataframe(df_btb_rack, hide_index=True, height=700, use_container_width=True)

        with title_btb_ww:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">LIST BIN TO BIN IN RACK {num_bin_ww}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

        with btb_ww:
            st.html(f"<span class='df_btb'</span>")
            st.dataframe(df_btb_ww, hide_index=True, height=400, use_container_width=True)
