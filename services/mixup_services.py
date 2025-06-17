import pandas as pd
from typing import Dict

class FindMixup:
	def __init__(self, df: pd.DataFrame):
		self.df = df.copy(deep=True)

	def get_mixup(self):
		"""	Lấy bin mixup 
			1. Lọc lấy toàn bộ vị trí kho MK
			2. Chỉ lấy vị trí rack wh1, wh2, wh3 trừ vị trí HO
			3. Chỉ lấy những dòng có duplicated location
			Logic lấy vị trí mixup
			1. Tạo 1 dict_loc chứa location vơi key là location và value là index df vừa lọc.
			Và 1 mask của df vừa lọc với giá trị là False
			2. Nếu location đã tồn tại trong dict_loc thì kiểm tra gcas, lot của hàng đang chạy và hàng
			trước đó
			3. So sánh nếu gcas hoặc lot của hàng hiện tại và hàng trước đó có khác nhau không?
			Nếu hợp lệ thì so sánh tiếp cat_inv của 2 dòng có phải cùng là 'eo' không, nếu có thì loại.
			Vì eo đang để mixup
			Nếu hợp lệ thì cập nhật mask là True ở vị trí hiện tại và vị trí trước đó thông qua loc trong pandas
			4. Xong thì đưa mask này vào df để lọc ra những vị trí đúng
		"""
		df_mixup = self.df

		mask = pd.Series(True, df_mixup.index)
		mask_mk = mask
		mask_wh = mask
		mask_duplicate = mask

		wh_mk = [f"pf{i}" for i in range(1, 6)] + [f"cool{i}" for i in range(1, 4)]
		mask_mk = df_mixup['name_wh'].isin(wh_mk)

		mask_wh = df_mixup['type_rack'].isin(['hr', 'pf'])
		mask_wh &= ~(df_mixup['type_loc'].isin(['ho']))

		mask_duplicate = df_mixup.duplicated(subset='location', keep=False)

		mask = (mask_mk|mask_wh)&(mask_duplicate)
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

		return df_mixup