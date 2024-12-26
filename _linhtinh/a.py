# import matplotlib.pyplot as plt


# # Tạo dữ liệu mẫu
# x = [1, 2, 3, 4, 5]
# y = [10, 20, 15, 25, 30]

# # Vẽ biểu đồ
# plt.plot(x, y)

# # Đặt số lượng điểm chia và nhãn cho trục x
# plt.xticks(range(1, 6), ['Label 1', 'Label 2', 'Label 3', 'Label 4', 'Label 5'])

# # Hiển thị biểu đồ
# plt.show()

# from database.conect_db import ConnectDB

# t = ConnectDB().getConection()
# import sys

# sys.path.insert(0, '/my_project/control')
# print(sys.path)
#=========================
# def my_decorator(func):
#     def wrapper(*args, **kwargs):
#         print("Something is happening before the function is called.")
#         result = func(*args, **kwargs)
#         print("Something is happening after the function is called.")
#         return result
#     return wrapper

# @my_decorator
# def say_hello():
#     print("Hello!")

# say_hello()

import re

str = 'Hoc lap trinh Toidicode.com'
match = re.search(r'(.*) Toidicode.com', str)
if match: #nếu tồn tại chuỗi khớp                     
    print (match.groups()) # in ra chuỗi đó
else:
    print ('Khong tim thay!') # Không thì hiện thông báo
#Kết quả:
#('Hoc lap trinh',)
import re

string = '39801 356, 2102 1111'

pattern = '(\d{3}) (\d{2})'

match = re.search(pattern, string)

if match: #nếu tồn tại chuỗi khớp
	print(match.group()) # in ra kết quả
	print(match.groups()) # in ra kết quả
	print(match.span()) # in ra kết quả

else:
  print("Không khớp") # Không thì hiện thông báo

