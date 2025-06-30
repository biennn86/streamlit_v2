import streamlit as st
import pandas as pd
import numpy as np
import re
from utils.constants import StatusBorder
from controllers.analytics_controller import AnalyticsController
from services.helper_services import normalize_data_upper

class TabDataViewer:
    def __init__(self, analytics_controller: AnalyticsController):
        self.analytics_controller = analytics_controller

    def render(self) -> None:
        self.df = self.analytics_controller.get_current_df_data()
        date_time = self.analytics_controller.get_datetime_current()

        #Check data
        if self.df.empty:
            st.info("No inventory data found in the database. Please import data first.")
            return
        
        cont_dataviewer = st.container(border=StatusBorder.BORDER.value)
        datasumary = cont_dataviewer.container(border=StatusBorder.BORDER.value)
        title_data_summary = cont_dataviewer.container(border=StatusBorder.BORDER.value)

        dataviewer = cont_dataviewer.container(border=StatusBorder.BORDER.value)
        title_dataviewer = dataviewer.container(border=StatusBorder.BORDER.value)

        
        # with title_dataviewer:
        #     col1, col2, col3 = title_data_summary.columns([1, 10, 1])
        #     with col2:
        #         st.html(f"<span class='title_dataviewer'</span>")
        #         st.subheader(f"CURRENT INVENTORY DATA {date_time}")
        
                
        with dataviewer:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">CURRENT INVENTORY DATA {date_time}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

            # st.html(f"<span class='data_viewer'</span>")
            # st.html(f"<span class='title_dataviewer'</span>")
            # st.subheader(f"CURRENT INVENTORY DATA {date_time}")
            
            
            self.df.index = range(1, len(self.df)+1)
            filtered_df = self.df.copy()

            col1, col2, col3, col4 = dataviewer.columns([1, 1, 1, 1])
            with col1:
                search_query = st.text_input("Search (e.g., by GCAS, Location, Description)", "")
            with col2:
                unique_namewh = filtered_df['name_wh'].unique().tolist()
                unique_namewh = [str(name).upper() for name in unique_namewh if name != '']
                unique_namewh.sort()
                selected_wh = st.selectbox("Filter by Warehouse", ["All"] + unique_namewh)
                
                if search_query:
                    mask = pd.Series(False, filtered_df.index)
                    for col in filtered_df.columns:
                        mask |= filtered_df[col].astype(str).str.contains(search_query.strip(), case=False, na=False)
                    filtered_df = filtered_df[mask]

                if selected_wh != "All":
                    selected_wh =selected_wh.lower()
                    filtered_df = filtered_df[filtered_df['name_wh'].isin([selected_wh])]

                self.df_sum = self.get_summary_filter(filtered_df)

            #Thông báo kết quả tìm kiếm
            # st.write(f"Showing **{len(filtered_df):,}** of {len(self.df):,} records after filtering.")
            st.markdown(
                f"<p style='margin-left: 0rem; padding-left: 0rem; margin-top: 1rem; margin-bottom: 0.5rem;'>Showing <b>{len(filtered_df):,}</b> of <b>{len(self.df):,}</b> records after filtering.</p>",
                unsafe_allow_html=True
            )
            # Display the filtered data
            df_display = self._edit_df_display(filtered_df)
            st.dataframe(df_display, use_container_width=True)
            self.download_data_display(df_display, selected_wh)

        with datasumary:
            # Header với container có thể control
            header_html  = f"""
            <div class="main-header" id="main-header">
                <div class="header-title">SUMMARY DATA {date_time}</div>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

            # st.subheader(f"SUMMARY DATA  {date_time}")
            st.dataframe(self.df_sum, use_container_width=True)
            st.divider()


    def _edit_df_display(self, df):
        df_dislay = df.copy()
        df_dislay = df_dislay[['gcas', 'description', 'batch', 'location', 'status', 'qty', 'pallet', 'name_wh']]
        df_dislay.columns = [re.sub(r'[ _-]', ' ', name).title().strip() for name in df_dislay.columns]
        df_dislay = normalize_data_upper(df_dislay)

        return df_dislay
    
    def get_summary_filter(self, df):
        if not df.empty:
            df_sm = pd.pivot_table(
                df,
                columns=['status'],
                index=['cat_inv'],
                values=['gcas', 'qty', 'pallet'],
                aggfunc={
                    'gcas': lambda x: x.nunique(),
                    'qty': 'sum',
                    'pallet': 'sum'
                },
                fill_value=0,
                margins=True,
                margins_name='Total'
            )

            # Tạo hàm định dạng
            def format_number_with_comma(x):
                if isinstance(x, (int, float)): # Đảm bảo chỉ định dạng số
                    return f"{int(x):,}" if x == int(x) else f"{x:,.2f}" # Định dạng số nguyên hoặc số thập phân 2 chữ số
                return x # Trả về giá trị gốc nếu không phải số (ví dụ: chuỗi, NaN)
            
            for col_level0, col_level1 in df_sm.columns:
                # Chọn cột cụ thể trong MultiIndex
                column_to_format = (col_level0, col_level1)
                
                # Áp dụng hàm định dạng cho cột đó
                df_sm[column_to_format] = df_sm[column_to_format].apply(format_number_with_comma)

            #Rename index và columns của df sau khi pivot_table
            df_sm = df_sm.rename_axis('Category', axis=0)
            df_sm = df_sm.rename(index={'eo': 'EO',
                                        'fg': 'FG',
                                        'rpm': 'RPM', 'cat_inv': 'aaaaa'}, level=0)
            
            df_sm = df_sm.rename(columns={'pallet': 'Pallet',
                                          'gcas': 'Gcas',
                                          'qty': 'Qty'}, level=0)

            df_sm = df_sm.rename(columns={'cat_inv': 'Category',
                                        'hd': 'HD',
                                        'rl': 'RL',
                                        'qu': 'QU'}, level=1)
            
            return df_sm
    
    def download_data_display(self, filtered_df, selected_warehouse):
        # Optional: Download filtered data
        if not filtered_df.empty:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Displayed Data as CSV",
                data=csv,
                file_name=f"inventory_data_{selected_warehouse.lower() if selected_warehouse != 'All' else 'all'}_{pd.Timestamp.now().strftime('%Y%m%d%H%M')}.csv",
                mime="text/csv",
                icon=":material/download:",
            )