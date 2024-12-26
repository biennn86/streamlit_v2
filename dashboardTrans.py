import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from readtrans.read_trans_rtcis import *
from control.data_after_analy import DataAnalys


def get_data_analys_from_sql():
    obj_data_after_analysis = DataAnalys()
    df_data = obj_data_after_analysis.get_df_from_db()

    return df_data

df = get_data_analys_from_sql()

st.set_page_config(page_title='Dashboard P&G', page_icon='📊', layout='wide') #page_icon='🎭'
st.title('Báo Cáo Tình Hình Hoạt Động Site P&G Trong Tuần/Tháng')
st.sidebar.header('Filter By:')
group = st.sidebar.multiselect('Filter By Group:',
                               options = df['group_user'].unique(),
                               default = df['group_user'].unique())
# date_shift = st.sidebar.multiselect('Filter By Date:',
#                                options=df['date_shift'].unique(),
#                                default=df['date_shift'].unique())
selection_query = df.query(
    'group_user == @group'
)
selection_query = selection_query.copy()

total_trans = selection_query['total_trans'].sum()
avg_trans = round(selection_query['total_trans'].mean(), 2)
cot1, buff, cot2 = st.columns([1, 0.5, 1])
with cot1:
    st.markdown('### Total Trans:')
    st.subheader(f'{total_trans:,}')
with cot2:
    st.markdown('### Average Trans:')
    st.subheader(f'{avg_trans:,.2f}')

st.markdown('---')

#1. tính sản lượng nhập theo ngày
selection_query['total_receive'] = selection_query['receive_wh_b'] +  selection_query['receive_234']
#tinh total_mhe
selection_query['total_mhe'] = selection_query['total_trans'] - \
    selection_query['total_receive'] - selection_query['move_stock'] - selection_query['scaner']
df_summary = selection_query.groupby(['date_shift']).agg({'total_receive': 'sum',
                                                'lta': 'sum',
                                                'scaner': 'sum',
                                                'total_mhe': 'sum',
                                                'total_trans': 'sum',
                                                }).reset_index()

#1.1 Tính lượng nhân sự nhập theo ngày
manpower = selection_query.groupby(['date_shift', 'group_user'])['user'].agg('count').reset_index()
manpower_inbound = manpower.query("group_user == 'Inbound'")#.reset_index(drop=True)
manpower_outbound = manpower.query("group_user == 'Outbound'")
manpower_mhe = manpower.query("group_user == 'MHE'")
manpower_total = selection_query.groupby(['date_shift'])['user'].agg('count').reset_index()
#phải merge lấy date_shift làm chuẩn tránh ca df khác bị thiếu dòng
df_summary = pd.merge(df_summary, manpower_inbound, left_on='date_shift', right_on='date_shift', how='left')
df_summary = pd.merge(df_summary, manpower_outbound, left_on='date_shift', right_on='date_shift', how='left', suffixes = ('_in', '_out'))
df_summary = pd.merge(df_summary, manpower_mhe, left_on='date_shift', right_on='date_shift', how='left')
df_summary = pd.merge(df_summary, manpower_total, left_on='date_shift', right_on='date_shift', how='left', suffixes = ('_mhe', '_total'))
#chèn 1 dòng mới vào df do ngày 24 inbound không có nhân sự
# df_chen = pd.DataFrame({'date_shift': '2024-03-24', 'group': 'Inbound', 'user': 0}, index=[0])
# manpower_inbound = pd.concat([manpower_inbound, df_chen], ignore_index=True)

# #2 Vẽ biểu đồ
st.bar_chart(df_summary, x='date_shift', y=['total_receive', 'lta', 'scaner'], 
             color=['#00ffff', '#2f4f4f', '#ffe4b5'],
             width=50, height=700, use_container_width=True)

class BuilChart():
    def __init__(self, df, title_desc, col_x, col_y1, col_y2, name_x, name_y1, name_y2, color_bar, width, height):
        self.df = df
        self.title_desc = title_desc
        self.col_x = col_x
        self.col_y1 = col_y1
        self.col_y2 = col_y2
        self.name_x = name_x
        self.name_y1 = name_y1
        self.name_y2 = name_y2
        self.color_bar = color_bar
        self.width = width
        self.height = height
    def draw_chart_bar_line(self):
        fig = go.Figure()
        fig.add_trace(go.Bar(x=self.df[self.col_x],
                                    y= self.df[self.col_y1],
                                    name= self.name_y1,
                                    marker_color=self.color_bar))
        fig.add_trace(go.Scatter(x= self.df[self.col_x],
                                        y = self.df[self.col_y2],
                                        mode = 'lines+markers',
                                        name = self.name_y2,
                                        line = dict(color='red'),
                                        yaxis= 'y2'))
        fig.update_layout(
            title=' ' * 10 + self.title_desc,
            xaxis_title=self.name_x,
            yaxis=dict(title=self.name_y1),
            yaxis2=dict(title=self.name_y2, overlaying='y', side='right', showgrid=False),
            autosize=False,
            width=self.width,
            height=self.height,
            )
        
        return fig

#bar_line outbound
title_out = 'Sản Lượng Xuất Theo Ngày Team Outbound'
arg_out = [df_summary, title_out, 'date_shift', 'scaner', 'user_out', 'Date', 'Pallet', 'Man', 'gold', 700, 400]
#bar_line inbound
title_in = 'Sản Lượng Nhập Theo Ngày Team Inbound'
arg_in = [df_summary, title_in, 'date_shift', 'total_receive', 'user_in', 'Date', 'Pallet', 'Man', 'greenyellow', 700, 400]  
#bar_line mhe
title_mhe = 'Sản Lượng Theo Ngày Team MHE'
arg_mhe = [df_summary, title_mhe, 'date_shift', 'total_mhe', 'user_mhe', 'Date', 'Pallet', 'Man', 'lime', 700, 400]  
#bar_line total
title_total = 'Total Sản Lượng Theo Ngày'
arg_total = [df_summary, title_total, 'date_shift', 'total_trans', 'user_total', 'Date', 'Pallet', 'Man', 'aqua', 700, 400]  

chart_out = BuilChart(*arg_out)
chart_in = BuilChart(*arg_in)
chart_mhe = BuilChart(*arg_mhe)
chart_total = BuilChart(*arg_total)

tab1, tab2, tab3, tab4 = st.tabs(['Total Team/MHE', 'Inboune/Outbound', 'Data Trans', 'Data Groupby'])
with tab1:
    col_mhe, buff, col_total = st.columns([2, 0.5, 2])
    with col_mhe:
        st.plotly_chart(chart_total.draw_chart_bar_line())
    with col_total:
        st.plotly_chart(chart_mhe.draw_chart_bar_line())
with tab2:
    col_in, buff,  cot_out = st.columns([2, 0.1, 2])
    with col_in:
        st.plotly_chart(chart_in.draw_chart_bar_line())
    with cot_out:
        st.plotly_chart(chart_out.draw_chart_bar_line())
with tab3:
    st.subheader('Tổng Hợp Transaction')
    st.dataframe(selection_query)
with tab4:
    st.subheader('Data Transaction Groupby')
    st.dataframe(df_summary, use_container_width=True)


# Hiển thị DataFrame
# st.write('Dữ Liệu Dataframe:', df.iloc[:, 0:28])

# # Tạo biểu đồ tương tác với Plotly
# fig = px.line(df, x='Date', y=['Value 1', 'Value 2'], title='Biểu đồ phức tạp')
# st.plotly_chart(fig, use_container_width=True)

# # Thêm thanh trượt cho người dùng chọn kích thước của biểu đồ
# num_points = st.slider('Số điểm trên biểu đồ:', min_value=10, max_value=len(df), value=50)

# # Cập nhật biểu đồ với số điểm được chọn
# fig_update = px.line(df[:num_points], x='Date', y=['Value 1', 'Value 2'], title='Biểu đồ phức tạp (cập nhật)')
# st.plotly_chart(fig_update, use_container_width=True)

#=================================================
# fig_receive = go.Figure()
# fig_receive.add_trace(go.Bar(x=df_summary['date_shift'],
#                      y= df_summary['total_receive'],
#                      name= 'Pallet',
#                      marker_color='mediumspringgreen'))
# fig_receive.add_trace(go.Scatter(x= df_summary['date_shift'],
#                          y = df_summary['user_in'],
#                          mode = 'lines+markers',
#                          name = 'Man',
#                          line = dict(color='red'),
#                          yaxis= 'y2'))
# fig_receive.update_layout(
#     title=' ' * 10 + 'Sản Lượng Nhập Theo Ngày Team Inbound',
#     xaxis_title='Date',
#     yaxis=dict(title='Pallet'),
#     yaxis2=dict(title='Man', overlaying='y', side='right', showgrid=False),
#     autosize=False,
#     width=750,
#     height=400,
# )
# st.plotly_chart(fig_receive)
