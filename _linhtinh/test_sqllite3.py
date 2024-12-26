import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('example.db')
c = conn.cursor()
# Tạo bảng
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')

# Thêm dữ liệu
c.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
c.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")

# Lưu thay đổi
conn.commit()

# Đóng kết nối
conn.close()

#=============
# Hàm thêm DataFrame vào cơ sở dữ liệu
def add_users_from_df(df):
    conn = sqlite3.connect('example.db')
    df.to_sql('users', conn, if_exists='append', index=False)
    conn.close()

def get_users_df():
    conn = sqlite3.connect('example.db')
    df = pd.read_sql_query('SELECT * FROM users', conn)
    conn.close()
    return df
#======================================
import streamlit as st
import pandas as pd
import sqlite3

# Hàm khởi tạo cơ sở dữ liệu và bảng users
def init_db():
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Đọc dữ liệu hiện có từ bảng users
df_existing = pd.read_sql_query("SELECT * FROM users", conn)

# Dữ liệu mới để cập nhật
df_new = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Dave'],
    'age': [31, 26, 40]
})

# Đóng kết nối tạm thời
conn.close()

# Hợp nhất dữ liệu mới với dữ liệu hiện có
df_combined = pd.concat([df_existing.set_index('name'), df_new.set_index('name')], axis=0, ignore_index=False)
df_combined = df_combined.reset_index().drop_duplicates(subset=['name'], keep='last')
# Hàm thêm hoặc cập nhật người dùng vào cơ sở dữ liệu
def upsert_user(name, age):
    # Kết nối đến cơ sở dữ liệu SQLite
    conn = sqlite3.connect('example.db')
    
    # Đọc dữ liệu hiện có từ bảng users
    df_existing = pd.read_sql_query("SELECT * FROM users", conn)
    
    # Dữ liệu mới để cập nhật
    df_new = pd.DataFrame({'name': [name], 'age': [age]})
    
    # Hợp nhất dữ liệu mới với dữ liệu hiện có
    df_combined = pd.concat([df_existing.set_index('name'), df_new.set_index('name')], axis=0, ignore_index=False)
    df_combined = df_combined.reset_index().drop_duplicates(subset=['name'], keep='last')
    
    # Chèn hoặc cập nhật dữ liệu vào bảng users
    df_combined.to_sql('users', conn, if_exists='replace', index=False)
    
    # Đóng kết nối
    conn.close()

# Hàm lấy dữ liệu từ bảng users và trả về DataFrame
def get_users_df():
    conn = sqlite3.connect('example.db')
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

# Khởi tạo cơ sở dữ liệu
init_db()

# Giao diện Streamlit
st.title('User Information')

# Hiển thị DataFrame từ cơ sở dữ liệu
df = get_users_df()
st.subheader('DataFrame')
st.write(df)

# Thêm hoặc cập nhật người dùng mới
st.subheader('Add or Update User')
new_name = st.text_input('Name')
new_age = st.number_input('Age', min_value=0, max_value=100, step=1)

if st.button('Add/Update User'):
    upsert_user(new_name, new_age)
    st.success('User added/updated successfully!')

    # Hiển thị lại DataFrame sau khi thêm người dùng mới
    df = get_users_df()
    st.write(df)


#=======================
# Thực hiện câu lệnh PRAGMA để lấy thông tin cột
c.execute(f"PRAGMA table_info({table_name})")
columns_info = c.fetchall()