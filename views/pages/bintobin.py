import streamlit as st
import pandas as pd
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
        self.df_btb = pd.DataFrame
        if button_btb:
            self.df_btb = self.bintobin_controller.run_bintobin(self.file_ton_kho_csv, self.file_demand)
        if not self.df_btb.empty:
            self.df_btb = self.df_btb.sort_values(by=["location"])
            st.dataframe(self.df_btb, hide_index=True, height=700, use_container_width=True)

    def render_page_btb(self):
        self.import_inv_prime_csv()
        self.import_file_demand()
        self.run_bintobin()
