import pandas as pd
from typing import Dict

class FindMixup:
	def __init__(self, df: pd.DataFrame):
		self.df = df.copy(deep=True)

	def _normalize_data(self, df: pd.DataFrame) -> None:
		"""Chuẩn hóa dữ liệu chuyển các cột text về uppercase
		"""
		string_columns = df.select_dtypes(include=['object', 'string'])
		for col in string_columns:
			#Chỉ áp dụng .str.upper() cho các Series kiểu object/string
			if pd.api.types.is_string_dtype(df[col]):
				#Chuyển về str và xử lý NaN
				df[col] = df[col].str.upper().astype(str).fillna('')
			elif isinstance(df[col], pd.Series): #Fallback cho các trường hợp khác có thể là object
				try:
					df[col] = df[col].astype(str).str.upper().fillna('')
				except Exception:
					pass # Bỏ qua nếu không chuyển đổi được
	
	def get_mixup(self):
		"""Lấy bin mixup 
		"""
		df_mixup = self.df

		# type_rack_notget = ('scanout', 'pick', 'reject', 'lrt', 'lslrm', 'lslpm', 'return', 'in')
		# for type_rack in type_rack_notget:
		# 	mask &= (df_mixup['type_rack'] != type_rack)
		
		mask = pd.Series(True, df_mixup.index)
		mask &= df_mixup['type_rack'].isin(['hr', 'pf', 'ww', 'mk'])
		mask &= (df_mixup['type_loc'] != 'ww')&(df_mixup['type_loc'] != 'ho')&(df_mixup['type_loc'] != 'fl')
		mask &= df_mixup.duplicated(subset='location', keep=False)

		df_duplicate_loc = df_mixup[mask]
		df_duplicate_loc = df_duplicate_loc.sort_values(by='location').reset_index(drop=True)
		
		dict_loc: Dict[str, int] = {}
		mask_mix = pd.Series(False, df_duplicate_loc.index)
		for i in range(len(df_duplicate_loc)):
			loc = df_duplicate_loc.loc[i, 'location']
			if loc not in dict_loc:
				dict_loc[loc] = i
			else:
				gcas_last = df_duplicate_loc.loc[dict_loc[loc], 'gcas']
				batch_last = df_duplicate_loc.loc[dict_loc[loc], 'batch']
				gcas_crr = df_duplicate_loc.loc[i, 'gcas']
				batch_crr = df_duplicate_loc.loc[i, 'batch']

				if any([(gcas_last != gcas_crr), (batch_last != batch_crr)]):
					cat_inv_last = df_duplicate_loc.loc[dict_loc[loc], 'cat_inv']
					cat_inv_crr = df_duplicate_loc.loc[i, 'cat_inv']
					if not (cat_inv_last == cat_inv_crr == 'eo'):
						mask_mix.iloc[dict_loc[loc]] = True
						mask_mix.iloc[i] = True

		df_mixup = df_duplicate_loc[mask_mix].reset_index(drop=True)

		#lấy cột cần hiển thị
		df_mixup = df_mixup[['date', 'gcas', 'description', 'location', 'batch', 'status', 'qty', 'pallet']]
		#viết hoa chữ cái đầu name columns
		df_mixup.columns = [col.capitalize() for col in df_mixup.columns]
		#Đánh lại số index
		df_mixup.index = range(1, len(df_mixup)+1)
		#viết hoa data striog, object trong df
		self._normalize_data(df_mixup)
		return df_mixup