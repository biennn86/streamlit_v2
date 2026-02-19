import streamlit as st
import pandas as pd
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController
from services.helper_services import normalize_data_upper

class TabEmptyLocView:
    #Lấy data từ controller
    # def __init__(self, analytics_controller: AnalyticsController):
    #     self.analytics_controller = analytics_controller

    #Lấy data từ state
    def __init__(self, data_emptyloc, datetime_current):
        self.data_emptyloc = data_emptyloc
        self.datetime_current = datetime_current

    def render(self) -> None:
        #Lấy data từ controller
        # self.df = self.analytics_controller.get_empty_location()
        # date_time = self.analytics_controller.get_datetime_current()
         #Lấy data từ state
        self.df = self.data_emptyloc
        date_time = self.datetime_current

        cont_emptyloc = st.container(border=StatusBorder.BORDER.value)
        title_emptyloc = cont_emptyloc.container(border=StatusBorder.BORDER.value)
        emptyloc = cont_emptyloc.container(border=StatusBorder.BORDER.value)

        with title_emptyloc:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">EMPTY LOCATION {date_time}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)
            # col1, col2, col3 = title_emptyloc.columns([1, 10, 1])
            # with col2:
            #     st.html(f"<span class='title_emp'</span>")
            #     st.subheader(f"EMPTY LOCATION {date_time}")
                
        with emptyloc:
            st.html(f"<span class='df_emp'</span>")
            st.dataframe(self._get_summary_emptyloc(), use_container_width=True)
            st.divider()
            st.dataframe(self._edit_display_dfemptyloc_view(), hide_index=True, height=700, use_container_width=True)
    
    def _edit_display_dfemptyloc_view(self):
        """ Edit lại các cột cần hiển thị lên dashboard
            Và upper lại datafame
        """
        df_view = self.df[['location', 'name_warehouse', 'location_usage_type', 'rack_usage_type', 'level', 'pallet_capacity']].reset_index(drop=False).copy()
        #Chèn thêm cột note
        df_view.insert(len(df_view.columns.to_list()), 'note', 'Empty')
        #đổi hr = Hight Rack, pf = Level A
        df_view['location_usage_type'] = df_view['location_usage_type'].map(
            {
                'hr': 'Hight Rack',
                'pf': 'Level A',
                'mk': 'Marking'
            }
        )
        #đổi tên rack_usage_type. DB = double deep, ST = Selective, FL = Floor, SV=Sheving
        df_view['rack_usage_type'] = df_view['rack_usage_type'].map(
            {
                'db': 'Double Deep',
                'st': 'Selective',
                'fl': 'Floor',
                'sv': 'Shelving',
                'ob': 'Obiter'
            }
        )
        #đổi tên cột
        df_view.rename(columns={
            'index': 'No',
            'location': 'Location',
            'location_usage_type': 'Level Code',
            'rack_usage_type': 'Type Location',
            'level': 'Level',
            'name_warehouse': 'WH Name',
            'pallet_capacity': 'Number Pallet',
            'note': 'Status'
        }, inplace=True)

        #chuyển thành chứ hoa
        df_view = normalize_data_upper(df_view)

        return df_view

    def _get_summary_emptyloc(self):
        """Lấy summary empty loc wh1, wh2, wh3 của hightrack và levelA
        """
        mask = pd.Series(True, self.df.index)
        mask &= self.df['name_warehouse'].isin(['wh1', 'wh2', 'wh3'])
        df  = self.df[mask].copy()
     
        df['pallet_capacity'] = pd.to_numeric(df['pallet_capacity'], downcast='integer')
        df_sm  = pd.pivot_table(
            df,
            columns=['location_usage_type', 'rack_usage_type'],
            index=['name_warehouse'],
            values=['pallet_capacity'],
            aggfunc='sum',
            fill_value=0,
            margins=True,
            margins_name='Grand Total'
        )

        #Rename index và columns của df sau khi pivot_table
        df_sm = df_sm.rename_axis('WH NAME', axis=0)
        df_sm = df_sm.rename(index={'wh1': 'WH1',
                                    'wh2': 'WH2',
                                    'wh3': 'WH3'}, level=0)
        
        df_sm = df_sm.rename(columns={'pallet_capacity': 'Pallet'}, level=0)
        df_sm = df_sm.rename(columns={'hr': 'Hight Rack',
                                      'pf': 'Level A'}, level=1)
        df_sm = df_sm.rename(columns={'db': 'Double Deep',
                                      'st': 'Selective',
                                      'ob': 'Rack DA',
                                      'ho': 'Hand Off',
                                      'sv': 'Shelving'}, level=2)
        return df_sm