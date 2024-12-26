import re
import pandas as pd
import sys
import time
from datetime import datetime

def get_data_form_dataframe(df):
	pattern_getrow = r'^(\w*|\s*)(([0-9]{2}\/){2}[0-9]{2}[\s][0-9:]+[\s][A-Z]+[^\S][0-9]+[-0-9]{2}[\s]+(F|P)[\s][0-9]+[\s][0-9A-Z]+[\s]*VN07[\s]+([0-9A-Z\s/#\\]){2,8}[\s]+[0-9-.]*[\s]*(EA|CS|NA|N\/A|#NA|#N\/A)?)'
	#Hàng mẫu: 03/02/24 07:28:41 DEPSUL 0010009772008339531-4  F 80772439 40610395P9    VN07     FF18A         32     CS
	#old: r'\W?\d{2}\/\d{2}\/\d{2}\s+\d+:\d+:\d+\s+[A-Z]+\s+\d+-\d{1}'
	#new_v1: r'\W?\d{2}\/\d{2}\/\d{2}\s+\d+:\d+:\d+\s+[A-Z]+\s+\d+-\d{1}\s+(F|P)\s+\d+\s+\d+\w+\s+(VN07)'
	#new_v2: r'^(\w*|\s*)(([0-9]{2}\/){2}[0-9]{2}[\s][0-9:]+[\s][A-Z]+[^\S][0-9]+[-0-9]{2}[\s]+(F|P)[\s][0-9]+[\s][0-9A-Z]+[\s]*VN07[\s]+([0-9A-Z\s/#\\]){2,8}[\s]+[0-9-.]*[\s]*(EA|CS|NA|N\/A|#NA|#N\/A)?)'
	#Set var 
	ROW_NULL = "nan"
	NUMBER_COLUMN = -1
	lst_result = []
	j=1
	for column in df.columns:
		NUMBER_COLUMN += 1
		for i in range(len(df[column]) - 1):
			data_row = df.iloc[i, NUMBER_COLUMN]
			# No read row null
			if str(data_row) == ROW_NULL:
				break

			try:
				check_row_get_match = re.match(pattern_getrow, data_row)
			except:
				# pass
				print("-------------------------------------------------------------------------------------------------")
				print("Data row i: {} , số dòng bị lỗi Match {}, cột: {}: {}".format(i, j, NUMBER_COLUMN, data_row))
				j += 1
	
			if check_row_get_match:
				data_row_not_user = check_row_get_match.group()
				data_row_user = df.iloc[i + 1, NUMBER_COLUMN]
				#clear_row
				string_row_cleared = get_row_from_data(data_row_not_user)
				if string_row_cleared is not None:
				# Lấy T#
					user_final = get_user_from_data(data_row_user)
				# Đưa kế quả vào list kết quả
					data_row_final = string_row_cleared + ";" + user_final + "\n"
					lst_result.append(data_row_final)
					data_row_final = None
					string_row_cleared = None
				else:
					pass
					# print("-" * 150)
					# print("Lỗi: {}, Data trả về None: {}".format(j, data_row_not_user))
					# print("Lỗi: {}, Data User: {}".format(j, data_row_user))
					# j += 1
			else:
				pass
				# print("-" * 150)
				# print("Lỗi: {}, Data không Match: {}".format(j, data_row))
				# j += 1
	return lst_result

def get_user_from_data(row_data_user):
	pattern_check_user = r'^[A-Z]{2,4}[0-9]{2,5}$'
	pattern_get_user = r'(?<=(Tech=))[A-Z0-9]{4,8}'
	NOT_FIND_USER = "UNKNOWN"
	global number_row_error
	try:
		match_user = re.search(pattern_get_user, row_data_user)
		if match_user:
			user = match_user.group()
		else:
			user = NOT_FIND_USER
			# print("."*150)
			# print("Row Number: {}, Data User Error: {}".format(i, row_data_user))
			# print("Row Number: {}, Data User Error: {}".format(i, data_row_not_user))
			# number_row_error += 1
		#check user sau khi clear
		check_user = re.match(pattern_check_user, user)
		if check_user:
			user_final = user
		else:
			user_final = NOT_FIND_USER

		return user_final
	except:
		# print("Row Number: {}, Data User Error: {}".format(number_row_error, row_data_user))
		# number_row_error += 1
		return NOT_FIND_USER

def get_row_from_data(row_data):
	try:
		index_cut = get_index_vn07(row_data)[1]
		left_row = row_data[:index_cut]
		right_row = row_data[index_cut:]

		left_row_fianl = process_left_row(left_row)
		category = left_row_fianl.split(";")[4]
		right_row_fianl = process_right_row(right_row, category)

		row_data_cleared = left_row_fianl + ";" + right_row_fianl
		
		if len(row_data_cleared.split(";")) == 11:
			return row_data_cleared
		else:
			return None
	except Exception:
		# print("Lỗi except hàm get_row: {}".format(row_data))
		return None
	
def process_left_row(left_row):
	try:
		left_row_clear = clear_one_space(left_row, ";")
		left_row_final = left_row_clear[0]
		
		return left_row_final
	except:
		return ""

def process_right_row(right_row, category):
	pattern_check_location = r'^\s*[A-Z]{1}[A-Z0-9/#\\]{1,7}$'
	pattern_check_digit = r'[0-9-.]{1,}'
	FG_CATEROGY = "F"
	PM_CATEGORY = "P"
	global number_row_error
	try:
		right_row_clear = clear_tow_space(right_row, ";")
		right_row_clear = clear_one_space(right_row_clear[0], "")
		lst_right_row = right_row_clear[0].split(";")
		lst_row_right_clear_none = [x  for x in lst_right_row if len(x) > 0]
		#Check right row
		len_list = len(lst_row_right_clear_none)
		if len_list == 1:
			check_loc = re.match(pattern_check_location, lst_row_right_clear_none[0])
			if check_loc and category == FG_CATEROGY:
				lst_row_right_clear_none.append('9999')
				lst_row_right_clear_none.append('CS')
			elif check_loc and category == PM_CATEGORY:
				lst_row_right_clear_none.append('9999')
				lst_row_right_clear_none.append('EA')
		elif len_list == 2:
			check_digit = re.match(pattern_check_digit, lst_row_right_clear_none[1])
			if check_digit:
				lst_row_right_clear_none.append('EA')
			else:
				lst_row_right_clear_none.insert(-1, '8888')
		elif len_list == 0 or len_list > 3:
			return ""
		
		left_row_final = ";".join(lst_row_right_clear_none)
		
		return left_row_final
	except:
		return ""
	
def get_index_vn07(row_data):
	pattern_get_vn07 = r'(\bVN07\b)'
	try:
		# phương thức span của re.search trả về tuple
		index_vn07_is_tuple = re.search(pattern_get_vn07, row_data).span()
		if index_vn07_is_tuple:
			return index_vn07_is_tuple
		else:
			return (0, 0)
	except:
		return (0, 0)
		

def clear_one_space(string_need_clear, string_replace):
	# Hàm subn trả về 1 tuple bao gồm string sau khi thay thế và số lượng vị trí đã thay
	# Nếu không tìm thấy sẽ trả về là chuỗi ban đầu và số lần thay thế là 0
	pattern_cut_onespace = r'(\s{1,})'
	try:
		string_clear_is_tuple = re.subn(pattern_cut_onespace, string_replace, string_need_clear)
		return string_clear_is_tuple
	except Exception:
		return (string_need_clear, 0)
	
def clear_tow_space(string_need_clear, string_replace):
	# Hàm subn trả về 1 tuple bao gồm string sau khi thay thế và số lượng vị trí đã thay
	# Nếu không tìm thấy sẽ trả về là chuỗi ban đầu và số lần thay thế là 0
	pattern_cut_towspace = r'(\s{2,})'
	try:
		string_clear_is_tuple = re.subn(pattern_cut_towspace, string_replace, string_need_clear)
		return string_clear_is_tuple
	except Exception:
		return (string_need_clear, 0)

def wire_data_to_txt(lst_data):
	with open ('data_tonghop_rtcis.txt', 'w') as file:
		file.writelines(lst_data)
		print("Đã hoàn thành ghi data ra file.")

def loading(i, total):
	percent = i / total * 100
	sys.stdout.write('\r')
	sys.stdout.write("[%-50s] %.2f%%" % ('-' * (int(percent) // 2), percent))
	sys.stdout.flush()

def time_loading(start, end):
	time_difference = end - start
	total_seconds = time_difference.total_seconds()
	minutes  = int(total_seconds // 60)
	seconds = round(int(total_seconds % 60),0)
	time_load = str(f'{minutes:02d}') + ":" + str(f'{seconds:02d}')
	return time_load

def main_clear_data_form_rtcis():
	starttime = datetime.now()
	path = 'D:/DATA/P&G/Documents/TXT_Python/phantichdata_withpandas/trans_PG/get_transaction_rtcis_070424 GuiMinh.xlsm'
	name_sh = 'DataFormRTCIS'
	df = pd.read_excel(path, sheet_name = name_sh)
	# df = pd.read_excel('data_rtcis_test.xlsx')
	# print(df.isna().sum())
	# df = df.fillna('Noname')
	
	lst_total_data_cleared = get_data_form_dataframe(df)


	print("Tổng số dòng tổng hợp được: {}".format(len(lst_total_data_cleared)))
	# print(lst_total_data_cleared)
	wire_data_to_txt(lst_total_data_cleared)
	endtime = datetime.now()
	time_diference = time_loading(starttime, endtime)
	print("Đã chạy xong, thời gian chạy: {}".format(time_diference))


number_row_error = 1
main_clear_data_form_rtcis()
# https://www.guru99.com/vi/python-regular-expressions-complete-tutorial.html