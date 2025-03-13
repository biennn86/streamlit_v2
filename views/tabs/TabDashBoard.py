import streamlit as st
from utils.constants import StatusBorder

class TabDashBoard:
    def showtab(self):
        container_inv = st.container(border=StatusBorder.BORDER.value)
        cont_dashboard = container_inv.container(border=StatusBorder.BORDER.value)
        cont_title = cont_dashboard.container(border=StatusBorder.BORDER.value)
        col_wh1, col_wh2, col_wh3, col_pf_cl, col_lable_total = cont_dashboard.columns([1, 1, 1, 1, 1])
        cont_metric = cont_dashboard.container(border=StatusBorder.BORDER.value)
        cont_wh1 = col_wh1.container(border=StatusBorder.BORDER.value)
        cont_wh2 = col_wh2.container(border=StatusBorder.BORDER.value)
        cont_wh3 = col_wh3.container(border=StatusBorder.BORDER.value)
        cont_pf_cl = col_pf_cl.container(border=StatusBorder.BORDER.value)
        cont_label_total = col_lable_total.container(border=StatusBorder.BORDER.value)

        

        
