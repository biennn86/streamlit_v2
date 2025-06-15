import pandas as pd

def normalize_data_lower(df) -> None:
    """Chuẩn hóa dữ liệu chuyển các cột text về lowrcase
    """
    string_columns = df.select_dtypes(include=['object', 'string'])
    for col in string_columns:
        #Chỉ áp dụng .str.lower() cho các Series kiểu object/string
        if pd.api.types.is_string_dtype(df[col]):
            #Chuyển về str và xử lý NaN
            df[col] = df[col].fillna('')
            df[col] = df[col].str.lower().astype(str)
        elif isinstance(df[col], pd.Series): #Fallback cho các trường hợp khác có thể là object
            try:
                df[col] = df[col].fillna('')
                df[col] = df[col].astype(str).str.lower()
            except Exception:
                pass # Bỏ qua nếu không chuyển đổi được
    return df

def normalize_data_upper(df) -> None:
    """Chuẩn hóa dữ liệu chuyển các cột text về lowrcase
    """
    string_columns = df.select_dtypes(include=['object', 'string'])
    for col in string_columns:
        #Chỉ áp dụng .str.lower() cho các Series kiểu object/string
        if pd.api.types.is_string_dtype(df[col]):
            #Chuyển về str và xử lý NaN
            df[col] = df[col].fillna('')
            df[col] = df[col].str.upper().astype(str)
        elif isinstance(df[col], pd.Series): #Fallback cho các trường hợp khác có thể là object
            try:
                df[col] = df[col].fillna('')
                df[col] = df[col].astype(str).str.upper()
            except Exception:
                pass # Bỏ qua nếu không chuyển đổi được
    return df