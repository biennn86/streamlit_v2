import pandas as pd
import csv
import re
from readtrans.analysis_data import *
from datetime import datetime, timedelta


class ReadDatatrans:
	def __init__(self, path_excel, sheet_name='DataFormRTCIS'):
		self.path_excel = path_excel
		self.sheet_name = sheet_name
		self.set_static_var()
		self.set_row_data = set()
		self.set_row_data_checkrepeat = set()
		self.dict_sequence_user_by_date = {}
		self.number_sequen = None

	def get_data_trans_from_excel(self):
		try:
			self.df = pd.read_excel(self.path_excel, self.sheet_name)
		except FileNotFoundError:
			print("File not found. Please provide a valid Excel file.")

		for column in self.df.columns:
			self.COLLUMN_NO += 1
			for i in range(len(self.df[column])-1):
				self.row_data_getform_df = self.df.iloc[i, self.COLLUMN_NO]

				if str(self.row_data_getform_df) == self.ROW_NULL:
					break

				try:
					check_row_get_match = self.pattern_getrow.match(self.row_data_getform_df)
				except:
					pass
					# print("-------------------------------------------------------------------------------------------------")
					# print("Data row i: {} , số dòng bị lỗi Match {}, cột: {}: {}".format(i, self.biendem, self.ROW_NULL, self.row_data_getform_df))
					# self.biendem += 1

				if check_row_get_match:
					self.data_row_not_user = check_row_get_match.group()
					self.data_row_user = self.df.iloc[i + 1, self.COLLUMN_NO]
					#Clear row
					self.string_row_cleared = self.get_row_from_data(self.data_row_not_user)
					if self.string_row_cleared is not None:
					# Get T#
						self.user_final = self.get_user_form_data(self.data_row_user)
					# Input results to list
						data_row_final = self.string_row_cleared + ";" + self.user_final
						if data_row_final not in self.set_row_data_checkrepeat:
							self.set_row_data_checkrepeat.add(data_row_final)

							str_days = self.string_row_cleared.split(';')[0]
							str_time = self.string_row_cleared.split(';')[1]
							key_date_user = self.get_days_shift_NS(str_days, str_time, self.user_final)

							if key_date_user in self.dict_sequence_user_by_date:
								self.dict_sequence_user_by_date[key_date_user] = self.dict_sequence_user_by_date[key_date_user] + 1
								self.number_sequen = self.dict_sequence_user_by_date.get(key_date_user)
							else:
								self.dict_sequence_user_by_date.setdefault(key_date_user, 1)
								self.number_sequen = 1

							data_row_final = self.string_row_cleared + ";" + self.user_final + ";" + str(self.number_sequen)
							self.set_row_data.add(data_row_final)
							# self.lst_results.append(data_row_final)
							#create dict data
							# dict_data = {}
							# data_row_insert = data_row_final.rstrip().split(";")
							# for i in range(len(self.lst_columns_datatrans)):
							# 	dict_data.setdefault(self.lst_columns_datatrans[i], data_row_insert[i])
							# if dict_data is not None:
							# 	self.data_trans.insert(dict_data)
							
							self.string_row_cleared = None
							data_row_final = None
							self.number_sequen = None
					else:
						pass
						# print("-" * 150)
						# print("Lỗi:, Data trả về None: {}".format(self.data_row_not_user))
				else:
					pass
					# print("-" * 180)
					# print("No: {}, Data không Match: {}".format(self.biendem, self.row_data_getform_df))
					# self.biendem += 1
		self.lst_results = list(self.set_row_data)
		return self.lst_results

	def get_days_shift_NS(self, str_day, str_time, str_user):
		'''
		Nếu giờ giao dịch từ 0:01 - 5:59 đây là giờ ca 3
		Hàm sẽ trừ ngày giao dịch lùi 1 ngày để xác định ca làm việc được chính xác
		'''
		cover_by_datetime = datetime.strptime(str_day + " " + str_time, '%m/%d/%y %H:%M:%S')
		days = cover_by_datetime.date()
		hour = cover_by_datetime.time().hour
		if 0 <= hour < 6:
			new_days = days - timedelta(days=1)
			str_days = datetime.strftime(new_days, '%m/%d/%y')
		else:
			str_days = datetime.strftime(days, '%m/%d/%y')
		return str_days + str_user

	def get_row_from_data(self, row_data):
		try:
			index_cut = self.get_index_vn07(row_data)[1]
			left_row = row_data[:index_cut]
			right_row = row_data[index_cut:]

			left_row_fianl = self.process_left_row(left_row)
			category = left_row_fianl.split(";")[4]
			right_row_fianl = self.process_right_row(right_row, category)

			row_data_cleared = left_row_fianl + ";" + right_row_fianl
			
			if len(row_data_cleared.split(";")) == 11:
				return row_data_cleared
			else:
				return None
		except Exception:
			# print("Lỗi except hàm get_row: {}".format(row_data))
			return None

	def process_left_row(self, left_row):
		try:
			left_row_clear = self.clear_one_space(left_row, ";")
			left_row_final = left_row_clear[0]

			return left_row_final
		except:
			return ""
		
	def process_right_row(self, right_row, category):
		pattern_check_location = r'^\s*[A-Z]{1}[A-Z0-9/#\\]{1,7}$'
		pattern_check_digit = r'[0-9-.]{1,}'
		FG_CATEROGY = "F"
		PM_CATEGORY = "P"
		global number_row_error
		try:
			right_row_clear = self.clear_tow_space(right_row, ";")
			right_row_clear = self.clear_one_space(right_row_clear[0], "")
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

	def get_user_form_data(self, row_data_user):
		NOT_FIND_USER = "UNKNOWN"
		try:
			match_user = self.pattern_get_user.search(row_data_user)
			if match_user:
				user = match_user.group()
			else:
				user = NOT_FIND_USER
				# print("."*150)
				# print("Row Number: {}, Data User Error: {}".format(i, row_data_user))
				# print("Row Number: {}, Data User Error: {}".format(i, data_row_not_user))
				# number_row_error += 1
			#check user sau khi clear
			check_user = self.pattern_check_user.match(user)
			if check_user:
				user_final = user
			else:
				user_final = NOT_FIND_USER

			return user_final
		except:
			# print("Row Number: {}, Data User Error: {}".format(number_row_error, row_data_user))
			# number_row_error += 1
			return NOT_FIND_USER

	def clear_one_space(self, string_need_clear, string_replace):
		# Hàm subn trả về 1 tuple bao gồm string sau khi thay thế và số lượng vị trí đã thay
		# Nếu không tìm thấy sẽ trả về là chuỗi ban đầu và số lần thay thế là 0
		try:
			string_clear_is_tuple = self.pattern_cut_onespace.subn(string_replace, string_need_clear)
			return string_clear_is_tuple
		except Exception:
			return (string_need_clear, 0)
	
	def clear_tow_space(self, string_need_clear, string_replace):
		# Hàm subn trả về 1 tuple bao gồm string sau khi thay thế và số lượng vị trí đã thay
		# Nếu không tìm thấy sẽ trả về là chuỗi ban đầu và số lần thay thế là 0
		try:
			string_clear_is_tuple = self.pattern_cut_towspace.subn(string_replace, string_need_clear)
			return string_clear_is_tuple
		except Exception:
			return (string_need_clear, 0)

	def get_index_vn07(self, data_row):
		try:
			# phương thức span của re.search trả về tuple
			self.index_vn07_is_tuple =self.pattern_get_vn07.search(data_row).span()
			if self.index_vn07_is_tuple:
				return self.index_vn07_is_tuple
			else:
				return (0, 0)
		except:
			return (0, 0)
		
	def create_df_from_list(self, list_results):
		title_df = ['date', 'time', 'activity', 'ulid', 'category', 'item', 'batch', 'plan', 'location', 'qty', 'unit', 'user', 'sequence']
		self.df_tonghopdata = pd.DataFrame(columns = title_df)
		df_list = []
		for data in list_results:
			data = data.split(";")
			data[-1] = data[-1].rstrip()
			data_tuple = tuple(data)
			series_data = pd.Series(data_tuple, index=title_df)
			df_list.append(series_data)

		self.df_tonghopdata = pd.concat(df_list, axis=1).T.reset_index(drop=True)
		# self.df_tonghopdata['batch'] = "'" + self.df_tonghopdata['batch']

		return self.df_tonghopdata
	
	def write_data_to_csv(self):
		try:
			self.df_tonghopdata.to_csv('data_trans_tonghop.csv', index=False, quoting=csv.QUOTE_ALL)
			print('Ghi data ra csv thành công')
		except AttributeError:
			print("DataFrame is not defined. Please read data from Excel first.")

	def write_data_to_txt(self):
		try:
			with open ('cls_data_tonghop_rtcis.txt', 'w') as file:
				file.writelines(self.lst_results)
				print("Đã hoàn thành ghi data ra file.")
		except FileNotFoundError:
			print("File not found. Please provide a valid TXT file.")

	def time_loading(self, start, end):
		time_difference = end - start
		total_seconds = time_difference.total_seconds()
		minutes  = int(total_seconds // 60)
		seconds = round(int(total_seconds % 60),0)
		time_load = str(f'{minutes:02d}') + ":" + str(f'{seconds:02d}')
		return time_load

	def set_static_var(self):
		self.COLLUMN_NO = -1
		self.ROW_NULL = "nan"
		self.lst_results = []
		self.biendem = 1
		self.pattern_get_vn07 = re.compile(r'(\bVN07\b)')
		self.pattern_cut_towspace = re.compile(r'(\s{2,})')
		self.pattern_cut_onespace = re.compile(r'(\s{1,})')
		self.pattern_check_user = re.compile(r'^[A-Z]{2,4}[0-9]{2,5}$')
		self.pattern_get_user = re.compile(r'(?<=(Tech=))[A-Z0-9]{4,8}')
		self.pattern_getrow = re.compile(r'^(\w*|\s*)(([0-9]{2}\/){2}[0-9]{2}[\s][0-9:]+[\s][A-Z]+[^\S][0-9]+[-0-9]{2}[\s]+(F|P)[\s][0-9]+[\s][0-9A-Z]+[\s]*VN07[\s]+([0-9A-Z\s/#\\]){2,8}[\s]+[0-9-.]*[\s]*(EA|CS|NA|N\/A|#NA|#N\/A)?)')
		self.lst_columns_datatrans = ['day', 'hour', 'activity', 'ulid', 'category', 'item', 'batch', 'plan', 'location', 'qty', 'unit', 'user']
		#Hàng mẫu: 03/02/24 07:28:41 DEPSUL 0010009772008339531-4  F 80772439 40610395P9    VN07     FF18A         32     CS
		#old: r'\W?\d{2}\/\d{2}\/\d{2}\s+\d+:\d+:\d+\s+[A-Z]+\s+\d+-\d{1}'
		#new_v1: r'\W?\d{2}\/\d{2}\/\d{2}\s+\d+:\d+:\d+\s+[A-Z]+\s+\d+-\d{1}\s+(F|P)\s+\d+\s+\d+\w+\s+(VN07)'
		#new_v2: r'^(\w*|\s*)(([0-9]{2}\/){2}[0-9]{2}[\s][0-9:]+[\s][A-Z]+[^\S][0-9]+[-0-9]{2}[\s]+(F|P)[\s][0-9]+[\s][0-9A-Z]+[\s]*VN07[\s]+([0-9A-Z\s/#\\]){2,8}[\s]+[0-9-.]*[\s]*(EA|CS|NA|N\/A|#NA|#N\/A)?)'
		# re lấy tồn kho
		# ^(?=\s*[0-9]{6})(.+)(?<=NONE)$


class DataframeIterator:
	def __init__(self, df):
		self.df = df
		self.data_by_row = []
	
	def interate(self):
		for index, row in self.df.iterrows():
			row_data = []
			for column in self.df.columns:
				row_data.append(row[column])
			self.data_by_row.append(row_data)
			
	def get_row(self, index):
		return self.data_by_row[index]

def test_df_inter():
	path_open_csv = "D:/DATA/P&G/my_project/file_source/data_trans_tonghop.csv"
	sheet_name = "data_trans_tonghop"
	data_analyzer = ReadCsvExcelToDataframe(path_open_csv)
	df = data_analyzer.read_csv_to_dataframe()
	df = df.drop_duplicates()

	df_iterator  = DataframeIterator(df)
	df_iterator.interate()
	row_2_data = df_iterator.get_row(2)
	print("Dữ liệu của hàng thứ 2:", row_2_data)

