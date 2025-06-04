import streamlit as st
from views.menu_appview import MenuApp
from views.tabs.TabDashBoard import *


class Tabs(MenuApp):
    def __init__(self):
        super().__init__()

    def setup_tab(self):
        self.tab_dashboard,\
        self.tab_emptyloc,\
        self.tab_combine,\
        self.tab_mixup,\
        self.tab_tonkho = st.tabs(['DashBoard', 'Empty Loc', 'Combine Bin', 'Mixup', 'Inventory'])

    def tab_dashboard(self, df_inventory):
        self.setup_tab()
        with self.tab_dashboard:
            TabDashBoard().showtab(df_inventory)
        