def parse_datetime(datetime_str):
    formats = [
    '%Y-%m-%d %H:%M:%S',  # 2024-05-25 14:30:00
    '%m/%d/%Y %I:%M:%S %p',  # 05/25/2024 02:30:00 PM
    '%d/%m/%Y %H:%M',  # 25/05/2024 14:30
    '%m/%d/%y %H:%M:%S',  # 05/25/24 14:30:00
    '%I:%M %p',  # 02:30 PM
    '%H:%M:%S',  # 14:30:00
]
    for fmt in formats:
        try:
            return pd.to_datetime(datetime_str, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(datetime_str, errors='coerce')  # Sử dụng `dateutil` như phương án cuối cùng, xử lý lỗi bằng cách trả về NaT


df_a['date_shift'] = df_a['date_shift'].apply(parse_datetime)