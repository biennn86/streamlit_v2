
# s = """ 
#  U 8604321
# """
# import re

# # pattern = r'^\s*[A-Z]{1}[A-Z0-9]{1,7}$')
# # pattern = r'(?<=(Tech=))[A-Z0-9]{4,8}'
# pt = r'b'

# # gr = re.match(pattern, s)
# # if gr:
# # 	print(gr.group())
# # 	print(gr)
# # else:
# # 	print("Không tìm thấy")

# sub = re.subn(pt, 'b', s)
# print(sub)
#----------------------------------------------------
# import pandas as pd

# # Tạo DataFrame mẫu
# data = {
#     'User': ['A', 'B', 'A', 'B', 'A'],
#     'Transaction_Time': ['08:30:00', '10:15:00', '12:45:00', '11:30:00', '09:00:00']
# }
# df = pd.DataFrame(data)

# # Chuyển cột 'Transaction_Time' sang kiểu datetime
# df['Transaction_Time'] = pd.to_datetime(df['Transaction_Time'])

# # Nhóm theo người dùng và tìm giờ giao dịch nhỏ nhất và lớn nhất
# result = df.groupby('User')['Transaction_Time'].agg([('Earliest_Transaction_Time', 'min'), ('Latest_Transaction_Time', 'max')])

# # In kết quả
# print(result)
#-------------------------------------------------------
# import pandas as pd

# # Tạo DataFrame mẫu
# data = {
#     'date': ['2024-04-01', '2024-04-03', '2024-04-02'],
#     'value': [10, 40, 70]
# }
# df = pd.DataFrame(data)
# print(df)
# # Sắp xếp DataFrame theo cột 'date' từ bé đến lớn và lưu thông tin về thứ tự sắp xếp
# df = df.sort_values(by='date', ascending=True).reset_index()

# print(df)
#---------------------------------------------------------
# import pandas as pd

# # Đọc dữ liệu từ file vào DataFrame
# df = pd.read_csv('du_lieu.csv')  # Thay 'du_lieu.csv' bằng tên file thực tế của bạn

# # Chuyển cột 'ngay_gio' sang định dạng datetime
# df['ngay_gio'] = pd.to_datetime(df['ngay_gio'])

# # Tạo một cột mới 'ca_lam_viec' để xác định ca làm việc cho mỗi giao dịch
# df['ca_lam_viec'] = pd.cut(df['ngay_gio'].dt.hour,
#                             bins=[0, 6, 14, 22, 24],
#                             labels=['Ca 3', 'Ca 1', 'Ca 2', 'Ca 3'])

# # Tính tổng thời gian làm việc cho mỗi người dùng theo từng ca làm việc
# thoi_gian_lam_viec = df.groupby(['user', 'ca_lam_viec']).size().unstack(fill_value=0)

# print(thoi_gian_lam_viec)
#------------------------------------------------------
# import pandas as pd

# hours = pd.Series(range(24))
# bins = [0, 6, 10, 14, 18, 22, 24]  # Giới hạn của các ca làm việc
# labels = ['Ca 3', 'Ca 1', 'Ca lỡ', 'Ca 12', 'Ca 2', 'Ca 2.12']  # Nhãn cho các ca làm việc

# ca_lam_viec = pd.cut(hours, bins=bins, labels=labels, ordered=False)
# print(ca_lam_viec)
#--------------------------------------------------------
# import pandas as pd

# # Tạo một DataFrame mẫu
# data = {'Group': ['A', 'A', 'B', 'B', 'C'],
#         'A': [1, 3, 2, 4, 5],
#         'B': [4, 2, 3, 1, 6],
#         'C': [7, 8, 9, 10, 11]}
# df = pd.DataFrame(data)

# # Định nghĩa hàm tính toán cho nhiều cột trong mỗi nhóm
# def custom_function(group):
# 	print(group)
#     # return group.iloc[:, 1:].sum()  # Truy cập các cột từ cột thứ 2 trở đi và tính tổng

# # Áp dụng hàm tính toán cho nhiều cột trong mỗi nhóm và lưu kết quả vào các cột mới
# df[['sum_A', 'sum_B', 'sum_C']] = df.groupby('Group').transform(custom_function)

# print(df)
#------------------------------------
# from datetime import datetime, timedelta
 
# # Tính toán khoảng thời gian ở tương lai và quá khứ
# future_date = datetime.now() + timedelta(days=10, hours=5, minutes=30)
# past_date = datetime.now() - timedelta(days=5, hours=2, minutes=15)
 
# # Định dạng và hiển thị khoảng thời gian
# future_formatted = future_date.strftime("%Y-%m-%d %H:%M:%S")
# past_formatted = past_date.strftime("%Y-%m-%d %H:%M:%S")
 
# # In kết quả
# print("Ngày trong tương lai định dạng:", future_formatted)
# print("Ngày trong quá khứ định dạng:", past_formatted)

#----------------------------------------
# import pandas as pd

# # Tạo DataFrame ví dụ
# df = pd.DataFrame({
#     'hour': ['2024-04-27 08:00:00', '2024-04-28 10:30:00', '2024-04-29 09:15:00']
# })

# # Chuyển cột 'hour' sang kiểu dữ liệu datetime
# df['hour'] = pd.to_datetime(df['hour'])

# # Chuyển các giá trị trong cột 'hour' thành giờ (loại bỏ ngày)
# df['hour'] = df['hour'].dt.time

# print(df)

#---------------------------------------------------

# Có một cách đơn giản để ghi nhớ sự khác biệt giữa axis=0 và axis=1 trong pandas là hình dung DataFrame như là một lưới, với các hàng và cột.

# axis=0 - Hàng:
# Khi bạn sử dụng axis=0, bạn đang thực hiện một phép tính hoặc thao tác trên các hàng của DataFrame.
# Điều này tương đương với việc di chuyển theo chiều dọc của lưới DataFrame, từ trên xuống dưới.
# axis=1 - Cột:
# Khi bạn sử dụng axis=1, bạn đang thực hiện một phép tính hoặc thao tác trên các cột của DataFrame.
# Điều này tương đương với việc di chuyển theo chiều ngang của lưới DataFrame, từ trái sang phải.
# Hình dung DataFrame như một bảng Excel: hàng là các hàng trong bảng và cột là các cột. Khi bạn sử dụng axis=0,
# bạn đang làm việc với các hàng, còn khi bạn sử dụng axis=1, bạn đang làm việc với các cột.

# Một cách nhớ khác có thể là nhớ rằng '0' trong axis=0 giống như dấu gạch ngang (-) trong biểu diễn toán học,
# nó liên quan đến dòng hoặc hướng dọc, trong khi '1' trong axis=1 giống như dấu gạch ngang (=), nó liên quan đến cột hoặc hướng ngang.

import pandas as pd

# df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
# df2 = pd.DataFrame({'A': [7, 8, 9], 'B': [10, 11, 12]})
df1 = pd.Series((1, 2, 3), index=['A', 'B', 'C'])
df2 = pd.Series((4, 5, 6), index=['A', 'B', 'C'])
df3 = pd.Series((7, 8, 9), index=['A', 'B', 'C'])


result = pd.concat([df1, df2, df3], axis=1).T.reset_index(drop=True)
print(result)