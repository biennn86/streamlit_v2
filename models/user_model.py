import datetime
import hashlib
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from models.table.tablename_database import *

class UserModel:
    '''Model xử lý dữ liệu người dùng'''
    def __init__(self):
        self.obj_user = TableNameUser()
        #Tạo table user và user admin
        # self._create_table_user()
    
    def _create_table_user(self) -> None:
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username varchar(50) NOT NULL UNIQUE,
                password_hash varchar(255) NOT NULL,
                email varchar(100) NOT NULL UNIQUE,
                fullname varchar(100),
                position varchar(100),
                address varchar(300),
                phone_number varchar(15),
                role varchar(20),
                is_active varchar(1),
                is_online varchar(1),
                udf1 varchar(1000),
                udf2 varchar(1000),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login_at DATETIME
            )
            """
        
        self.obj_user.create_table(create_table_sql)
        #Tạo user admin
        create_user_admin = {
            'username': 'admin',
            'password_hash': 'admin',
            'email': 'biennn86@gmail.com',
            'fullname': 'Nguyen Ngoc Bien',
            'position': 'OPS',
            'address': 'WH PG',
            'phone_number': '0908336586',
            'role': 'admin',
            'is_active': 1,
            'is_online': 0,
            'udf1': 'Ngày 13/03/2023 qua PG làm việc với vai trò hỗ trợ viết jobaid cho Nghi. Đến 05/2023 bắt đầu làm việc ở vị trí suppervisor'

        }
        self.insert_user(create_user_admin)

        #Tạo user edit
        create_user_edit = {
            'username': 'edit',
            'password_hash': 'edit123',
            'email': 'edit@gmail.com',
            'fullname': 'Nguyen Van Edit',
            'position': 'OPS',
            'address': 'WH PG',
            'phone_number': '0123456789',
            'role': 'edit',
            'is_active': 1,
            'is_online': 0,
            'udf1': 'User này có quyền edit'

        }
        self.insert_user(create_user_edit)

        #Tạo user edit
        create_user_view = {
            'username': 'view',
            'password_hash': 'view123',
            'email': 'view@gmail.com',
            'fullname': 'Nguyen Van View',
            'position': 'OPS',
            'address': 'WH PG',
            'phone_number': '0123456789',
            'role': 'viewer',
            'is_active': 1,
            'is_online': 0,
            'udf1': 'User này có quyền view'

        }
        self.insert_user(create_user_view)

        #Tạo user demo
        create_user_demo = {
            'username': 'demo',
            'password_hash': 'demo123',
            'email': 'demo@gmail.com',
            'fullname': 'Nguyen Van Chi Xem',
            'position': 'OPS',
            'address': 'WH PG',
            'phone_number': '0123456789',
            'role': 'guest',
            'is_active': 1,
            'is_online': 0,
            'udf1': 'User này có quyền xem tab Dashboard'

        }
        self.insert_user(create_user_demo)

        # create_trigger_sql = f"""
        #     CREATE TRIGGER IF NOT EXISTS update_updated_at_trigger
        #     AFTER UPDATE ON user
        #     FOR EACH ROW
        #     BEGIN
        #         UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        #     END;
        #     """
        # self.user_db.create_table(create_trigger_sql)
    
    def insert_user(self, dict_data_user) -> bool:
        # Lấy ngày giờ hiện tại
        current_datetime = datetime.datetime.now()
        # Định dạng đối tượng datetime thành chuỗi
        formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # Lấy password để mã hóa qua md5
        password = dict_data_user.get("password_hash", None)

        if password:
            # Mã hóa password
            dict_data_user["password_hash"] = self._hash_password(password)
            # Add data user after insert to database
            # Add data created_at, updated_at, last_login_at
            dict_data_user["created_at"] = formatted_string
            dict_data_user["updated_at"] = formatted_string
            dict_data_user["last_login_at"] = None

            self.obj_user.insert_user(data=dict_data_user)
            return True
        return False
    
    def update_last_login(self, username) -> bool:
        user = self.get_user_info(username=username)
        if user:
            # Lấy ngày giờ hiện tại
            current_datetime = datetime.datetime.now()
            # Định dạng đối tượng datetime thành chuỗi
            formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            self.obj_user.update_user(username=username, data={"last_login_at": formatted_string})
            return True
        return False
    
    
    def delete_user(self, username) -> bool:
        user = self.obj_user.get_user_info(username)
        if user:
            self.obj_user.delete_user(username=username)
            return True
        return False

    def _hash_password(self, password) -> str:
        """Mã hóa password (đơn giản)"""
        return hashlib.md5(password.encode()).hexdigest()

    def validate_credentials(self, username, password) -> bool:
        """Validate thông tin đăng nhập"""
        user = self.obj_user.get_user_info(username)
        if user and user['password_hash'] == self._hash_password(password):
            return True
        return False
    
    def get_user_info(self, username) -> Dict:
        """Lấy thông tin user"""
        return self.obj_user.get_user_info(username)
    
    def get_user_role(self, username) -> str:
        """Lấy role của user"""
        user = self.obj_user.get_user_info(username)
        return user['role'] if user else 'guest'
    
    def get_user_active(self, username) -> int:
        """Lấy role của user"""
        user = self.obj_user.get_user_info(username)
        return user['is_active'] if user else 0
    
    def update_user_profile(self, username, profile_data) -> bool:
        """Cập nhật profile user"""
        # Lấy ngày giờ hiện tại
        current_datetime = datetime.datetime.now()
        # Định dạng đối tượng datetime thành chuỗi
        formatted_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        user = self.obj_user.get_user_info(username)
        if user:
            profile_data["updated_at"] = formatted_string
            self.obj_user.update_user(username=username, data=profile_data)
            return True
        return False
    
    def get_all_users(self) -> pd.DataFrame:
        """Lấy danh sách tất cả users (cho admin)"""
        df_all_user = self.obj_user.read_to_dataframe()
        if df_all_user:
            return df_all_user
        return pd.DataFrame