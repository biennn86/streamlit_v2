# import matplotlib.pyplot as plt
# import pandas as pd

# # Giả sử df là DataFrame của bạn
# df = pd.DataFrame({'Ngày': range(1, 32),
#                    'Sản lượng nhập': range(30, 61),
#                    'Sản lượng xuất': range(45, 76),
#                    'Tồn kho': range(23, 54)})
# # Chuyển đổi cột 'Ngày' sang kiểu dữ liệu datetime
# df['Ngày'] = pd.to_datetime('2024-05-' + df['Ngày'].astype(str))
# print(df)


# # Sắp xếp DataFrame theo cột 'Ngày' nếu cần
# df = df.sort_values(by='Ngày')


# # Đặt kích thước của biểu đồ
# plt.figure(figsize=(14, 6))  # Đặt chiều rộng lớn hơn để phù hợp với 31 ngày

# # Đặt chiều rộng của các cột
# bar_width = 0.2

# cot1 = range(0, len(df['Ngày']))
# cot2 = [x + bar_width for x in cot1]
# cot3 = [x + bar_width for x in cot2]

# # Vẽ biểu đồ
# plt.bar(cot1, df['Sản lượng nhập'], width=bar_width, align='center', label='Sản lượng nhập')
# plt.bar(cot2, df['Sản lượng xuất'], width=bar_width, align='center', label='Sản lượng xuất')
# plt.bar(cot3, df['Tồn kho'], width=bar_width, align='center', label='Tồn kho')

# # Đặt nhãn cho trục x và trục y
# plt.xlabel('Ngày')

# plt.ylabel('Sản lượng')

# # Đặt tiêu đề cho biểu đồ
# plt.title('Sản lượng nhập, sản lượng xuất và tồn kho theo ngày trong tháng 5/2024')

# # Thêm chú thích
# plt.legend()

# # Định dạng trục x để hiển thị ngày tháng
# plt.xticks(df.index, df['Ngày'].dt.strftime('%Y-%m-%d'), rotation=90)

# # Hiển thị biểu đồ
# plt.tight_layout()
# plt.show()

#====================================
# import pandas as pd

# # Tạo DataFrame mẫu
# data = {
#     'A': [1, 2, 3],
#     'B': [4, 5, 6]
# }
# df = pd.DataFrame(data)

# # Dữ liệu cho dòng mới
# new_row = {'A': 7, 'B': 8}

# # Chèn dòng mới vào DataFrame
# df = df.append(new_row, ignore_index=True)

# print(df)
#============================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Tạo dữ liệu mẫu
data = {
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Values': [10, 20, 15, 25, 30],
    'Trend': [8, 18, 12, 22, 28]
}
df = pd.DataFrame(data)

# Tạo biểu đồ
fig = go.Figure()

# Vẽ bar chart
fig.add_trace(go.Bar(x=df['Category'], y=df['Values'], name='Values', marker_color='lightblue'))

# Vẽ line chart cho trend trên trục y
fig.add_trace(go.Scatter(x=df['Category'], y=df['Trend'], mode='lines+markers', name='Trend', line=dict(color='red'), yaxis='y2'))

# Thiết lập layout
fig.update_layout(
    title='Bar and Line Chart Combination',
    xaxis_title='Category',
    yaxis=dict(title='Values'),  # Trục y chính
    yaxis2=dict(title='Trend', overlaying='y', side='right', showgrid=False)  # Trục y phụ
)

# Hiển thị biểu đồ
st.plotly_chart(fig)

#===============================
import streamlit as st
import pandas as pd
import plotly.express as px

# Tạo dữ liệu mẫu
data = {
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Values': [10, 20, 15, 25, 30],
    'Trend': [8, 18, 12, 22, 28]
}
df = pd.DataFrame(data)

# Vẽ biểu đồ
fig = px.bar(df, x='Category', y='Values', labels={'Values': 'Values'}, color_discrete_sequence=['lightblue'])
fig.add_trace(px.line(df, x='Category', y='Trend', labels={'Trend': 'Trend'}).data[0])

# Thiết lập tiêu đề và nhãn trục
fig.update_layout(title='Bar and Line Chart Combination', xaxis_title='Category', yaxis_title='Values/Trend')

# Hiển thị biểu đồ
st.plotly_chart(fig)
 #========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Tạo dữ liệu mẫu
data = {
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Values': [10, 20, 15, 25, 30],
    'Trend': [8, 18, 12, 22, 28]
}
df = pd.DataFrame(data)

# Tạo biểu đồ cột
fig_bar = px.bar(df, x='Category', y='Values', labels={'Values': 'Values'}, color_discrete_sequence=['lightblue'])

# Tạo biểu đồ đường cho trend
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=df['Category'], y=df['Trend'], mode='lines+markers', name='Trend', yaxis='y2', line=dict(color='red')))

# Kết hợp hai biểu đồ
fig = go.Figure(fig_bar.data + fig_line.data)

# Thiết lập layout
fig.update_layout(
    title='Bar and Line Chart Combination',
    xaxis_title='Category',
    yaxis=dict(title='Values'),  # Trục y chính
    yaxis2=dict(title='Trend', overlaying='y', side='right', showgrid=False)  # Trục y phụ
)

# Hiển thị biểu đồ
st.plotly_chart(fig)
