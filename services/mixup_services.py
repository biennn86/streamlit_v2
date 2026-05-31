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
			1. Tạo 1 dict_loc chứa location với key là location và value là index df vừa lọc.
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
		#Chuẩn bị df: loại ỏ những vị trí không cần thiết khi đi tìm mixup
		mask = pd.Series(True, df_mixup.index)
		mask_mk = mask
		mask_wh = mask
		mask_duplicate = mask

		wh_mk = [f"pf{i}" for i in range(1, 6)] + [f"cool{i}" for i in range(1, 4)]
		mask_mk = df_mixup['name_warehouse'].isin(wh_mk)

		mask_wh = df_mixup['location_system_type'].isin(['hr', 'pf'])
		mask_wh &= ~(df_mixup['rack_usage_type'].isin(['ho']))

		mask_duplicate = df_mixup.duplicated(subset='location', keep=False)

		mask = (mask_mk|mask_wh)&(mask_duplicate)
		df_duplicate_loc = df_mixup[mask]
		df_duplicate_loc = df_duplicate_loc.sort_values(by='location').reset_index(drop=True)
		#Đi tìm vị trí mixup
		# 1. Nhóm theo 'location' và đếm số lượng tổ hợp [gcas, batch, status] duy nhất tại mỗi vị trí
		# Hàm nunique() sẽ bỏ qua các dòng trùng lặp hoàn toàn của cùng một loại hàng
		mixup_counts = df_duplicate_loc.groupby('location')[['gcas', 'batch', 'status']].nunique()

		# 2. Một vị trí bị mixup nếu CÓ ÍT NHẤT một trong 3 cột trên có số lượng giá trị duy nhất > 1
		is_mixup = (mixup_counts['gcas'] > 1) | (mixup_counts['batch'] > 1) | (mixup_counts['status'] > 1)

		# 3. Lấy ra danh sách các vị trí bị mixup
		mixup_locations = mixup_counts[is_mixup].index.tolist()
		
		# 4. (Tùy chọn) Trích xuất toàn bộ dữ liệu chi tiết của các vị trí bị mixup để bạn dễ kiểm tra
		df_mixup_detail = df_duplicate_loc[df_duplicate_loc['location'].isin(mixup_locations)].sort_values(by='location')
		# 5. Bỏ những vị trí mixup có cat_inv cùng là eo. Nếu vị trí mixp 1 pallet fg|rpm và 1 pallet eo vẫn giữ lại
		# 5.1. VECTOR HÓA BỘ LỌC CAT_INV: Kiểm tra xem vị trí đó có phải chỉ chứa toàn hàng 'eo' hay không
		# Ta đếm tổng số pallet tại mỗi vị trí và số pallet là 'eo' tại vị trí đó
		cat_check = df_mixup_detail.groupby('location')['cat_inv'].agg(
			total_pallets='count',
			eo_pallets=lambda x: (x == 'eo').sum()
		)

		# Vị trí bị coi là "chỉ chứa toàn eo" khi số pallet 'eo' bằng đúng tổng số pallet tại đó
		only_eo_locations = cat_check[cat_check['total_pallets'] == cat_check['eo_pallets']].index

		# 5.2. Loại bỏ các vị trí chỉ chứa toàn hàng 'eo' ra khỏi danh sách mixup
		df_final_mixup = df_mixup_detail[~df_mixup_detail['location'].isin(only_eo_locations)].copy()
		return df_final_mixup
	
'''
# 1. Nhóm theo 'location' và đếm số lượng tổ hợp [gcas, batch, status] duy nhất tại mỗi vị trí
# Hàm nunique() sẽ bỏ qua các dòng trùng lặp hoàn toàn của cùng một loại hàng
mixup_counts = df.groupby('location')[['gcas', 'batch', 'status']].nunique()

# 2. Một vị trí bị mixup nếu CÓ ÍT NHẤT một trong 3 cột trên có số lượng giá trị duy nhất > 1
is_mixup = (mixup_counts['gcas'] > 1) | (mixup_counts['batch'] > 1) | (mixup_counts['status'] > 1)

# 3. Lấy ra danh sách các vị trí bị mixup
mixup_locations = mixup_counts[is_mixup].index.tolist()

# 4. (Tùy chọn) Trích xuất toàn bộ dữ liệu chi tiết của các vị trí bị mixup để bạn dễ kiểm tra
df_mixup_detail = df[df['location'].isin(mixup_locations)].sort_values(by='location')

'''
'''
Giải thích chi tiết cách code vận hành
Hãy giả sử tại vị trí kho LOC-01 bạn có 3 dòng dữ liệu sau:
1.	gcas=A, batch=10, status=OK
2.	gcas=A, batch=10, status=OK (Dòng này trùng hoàn toàn dòng 1, bản chất vẫn là 1 loại hàng)
3.	gcas=A, batch=20, status=OK (Khác batch -> Bị mixup)
Khi chạy qua hàm xử lý:
•	df.groupby('location')['gcas'].nunique() sẽ trả về: 1 (chỉ có duy nhất mặt hàng A).
•	df.groupby('location')['batch'].nunique() sẽ trả về: 2 (gồm batch 10 và batch 20).
•	Do cột batch có kết quả là 2 > 1, điều kiện is_mixup lập tức được thỏa mãn và gắn cờ vị trí LOC-01 này bị trộn hàng.
Kết quả bạn nhận được:
•	mixup_locations: Trả về một List chứa tên các vị trí bị mixup (ví dụ: ['LOC-01', 'LOC-05']).
•	df_mixup_detail: Trả về một DataFrame chứa toàn bộ các dòng hàng đang nằm sai vị trí tại các ô kho bị mixup đó để bạn xuất báo cáo hoặc đi xử lý thực tế.

'''
'''
CÁCH NGUYÊN THỦY CHƯA VECTOR HÓA
		# dict_loc: Dict[str, int] = {}
		# mask_mix = pd.Series(False, df_duplicate_loc.index)

		# for i in range(len(df_duplicate_loc)):
		# 	loc = df_duplicate_loc.loc[i, 'location']
		# 	if loc not in dict_loc:
		# 		dict_loc[loc] = i
		# 	else:
		# 		gcas_last = df_duplicate_loc.loc[dict_loc[loc], 'gcas']
		# 		batch_last = df_duplicate_loc.loc[dict_loc[loc], 'batch']
		# 		gcas_crr = df_duplicate_loc.loc[i, 'gcas']
		# 		batch_crr = df_duplicate_loc.loc[i, 'batch']

		# 		if any([(gcas_last != gcas_crr), (batch_last != batch_crr)]):
		# 			cat_inv_last = df_duplicate_loc.loc[dict_loc[loc], 'cat_inv']
		# 			cat_inv_crr = df_duplicate_loc.loc[i, 'cat_inv']
		# 			if not (cat_inv_last == cat_inv_crr == 'eo'):
		# 				mask_mix.iloc[dict_loc[loc]] = True
		# 				mask_mix.iloc[i] = True

		# df_mixup = df_duplicate_loc[mask_mix].reset_index(drop=True)

		# return df_mixup

'''