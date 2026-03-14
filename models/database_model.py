import sqlite3
import os
from sqlalchemy import create_engine, text
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    ''' Quản lý kết nối và hoạt động của database
        Sử dụng kết nối bằng module sqlalchemy
    '''
    __PATH_DB_ON_SOURCE = "database/pg.db"
    __PATH_DB_LOCAL_ON_DISK = "D:\P&G\dashboard\my_database\db_pg.db"
    __PATH_DB = None
    def __init__(self):
        """Khỏi tạo quản lý database
        Args:
            None
        """
        self.table = None
        self.connection = None
        # self.cursor = None
        # self.df_import = None

    def connect(self) -> None:
        """ Thiết lập kết nối tới database
            Tối ưu SQLite connection để tăng tốc
        """
        try:
            #Lấy path database trên máy nếu chạy local, lấy trong file nguồn nếu chạy streamlit could
            if os.path.exists(self.__PATH_DB_LOCAL_ON_DISK):
                self.__PATH_DB = self.__PATH_DB_ON_SOURCE
            else:
                self.__PATH_DB = self.__PATH_DB_ON_SOURCE

            engine = create_engine(f'sqlite:///{self.__PATH_DB}', 
                          connect_args={
                              'check_same_thread': False,
                              'timeout': 30
                          })
            # Tối ưu SQLite settings
            with engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode = WAL"))
                conn.execute(text("PRAGMA synchronous = NORMAL"))
                conn.execute(text("PRAGMA cache_size = 100000"))
                conn.execute(text("PRAGMA temp_store = MEMORY"))

            self.connection = engine.connect()

            logger.info(f"Connected to database with table {self.table}")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def disconnect(self) -> None:
        """Đóng kết nối tới database"""
        if self.connection:
            self.connection.close()
            logger.info(f"Database connection closed with table {self.table}")
            self.connection = None
            # self.cursor = None

    def create_table(self, create_table_sql) -> None:
        try:
            self.connect()
            self.connection.execute(text(create_table_sql))
            self.connection.commit()
            logger.info(f"Table '{self.table}' created or confirmed existing")
            return True
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return None
        finally:
            self.disconnect()

    def insert_user(self, data) -> None:
        try:
            self.connect()
            columns = ', '.join(list(data.keys()))
            placeholders = ', '.join([f':{col}' for col in data.keys()])
            sql = f"INSERT INTO {self.table}({columns}) VALUES ({placeholders})"
            self.connection.execute(text(sql), data)
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error insert data to table {self.table}: {e}")
            return None
        finally:
            self.disconnect()

    def update_user(self, username, data) -> None:
        # SQL được tạo ra:
        # UPDATE user SET email = :email, phone_number = :phone_number WHERE username = :username

        # values truyền vào:
        # {'email': 'newemail@example.com', 'phone_number': '0987654321', 'username': 'admin'}
        try:
            self.connect()
            data_updates = []
            for key in data.keys():
                data_updates.append(f"{key} = :{key}")
            data['username'] = username
            sql = f"UPDATE {self.table} SET {', '.join(data_updates)} WHERE username = :username"
            self.connection.execute(text(sql), data)
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error update data to table {self.table}: {e}")
            return None
        finally:
            self.disconnect()

    def delete_user(self, username) -> None:
        try:
            self.connect()
            sql = f"DELETE FROM {self.table} WHERE username = :username"
            self.connection.execute(text(sql), {'username': username})
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error delete data {self.table}: {e}")
            return None
        finally:
            self.disconnect()
    
    def get_user_info(self, username) -> Dict[any, any]:
        try:
            self.connect()
            sql = f"SELECT * FROM {self.table} WHERE username = :username"
            result = self.connection.execute(text(sql), {"username": username}).mappings().first()

            #Nếu không không có data trong table thì dict() sẽ báo lỗi vì kết quả trả về Nonetype
            #Nên phải bắt lỗi đó
            if result is None:
                logger.warning(f"User '{username}' không có data trong database.")
                return None
            return result
        except Exception as e:
            logger.error(f"Error get data from table {self.table}: {e}")
            return None
        finally:
            self.disconnect()
        
    def read_to_dataframe(self)-> pd.DataFrame:
        """Lấy data trong database theo table name
            SELECT * FROM inventory ORDER BY rowid DESC LIMIT 20000;
        Resuls:
            pd.DataFrame
        """
        try:
            self.connect()
            QUERY = f"SELECT * FROM {self.table}"
            df = pd.read_sql_query(QUERY, self.connection)
            logger.info(f"Read {len(df)} rows form table {self.table}")
            return df
        except Exception as e:
            logger.error(f"Error reading table: {e}")
            return None
        finally:
            self.disconnect()

    def insert_dataframe_new_only(self, df_new: pd.DataFrame) -> None:
        """
            Chỉ insert những dòng chưa tồn tại - nhanh nhất
            key_columns: list các cột dùng làm key để check duplicate
        """
        try:
            # Drop the table if it exists and recreate it
            # self.connect()
            # self.connection.execute(f"DROP TABLE IF EXISTS 'inventory'")
            # self.disconnect()

            #tên bảng tạm
            temp_table = f"{self.table}_temp"
            # Import vào bảng tạm
            self.connect()
            df_new.to_sql(temp_table, self.connection, if_exists='replace', 
                  index=False, method='multi', chunksize=1000)
            
            #tên cột cần lọc trùng
            key_columns = []
            if self.table in ['inventory']:
                key_columns = ['date']
            elif self.table in ['master_data']:
                key_columns = ['gcas', 'bd_plt_pat']
            elif self.table in ['master_location_new', 'master_location']:
                key_columns = ['location']

            # Tạo index cho bảng tạm
            for col in key_columns:
                self.connection.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{temp_table}_{col} ON {temp_table}({col})"))
            
            # Chỉ insert những dòng chưa tồn tại
            join_condition = ' AND '.join([f"t.{col} = m.{col}" for col in key_columns])

            query = f"""
            INSERT INTO {self.table} 
            SELECT t.* FROM {temp_table} t
            LEFT JOIN {self.table} m ON {join_condition}
            WHERE m.{key_columns[0]} IS NULL
            """

            result = self.connection.execute(text(query))

             # Xóa bảng tạm
            self.connection.execute(text(f"DROP TABLE {temp_table}"))
            self.connection.commit()

            return result.rowcount
            
        except Exception as e:
            logger.error(f"Unexpected error during data insertion: {e}")
            raise
        finally:
            self.disconnect()

    def create_indexes(self, key_columns) -> None:
        """
        Tạo index trên các cột key
        """
        try:
            self.connect()
            for col in key_columns:
                self.connection.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table}_{col} 
                    ON {self.table}({col})
                """))
            self.connection.commit()
            logger.info(f"Created indexes for table: {self.table}")
        except Exception as e:
            logger.error(f"Create indexes error: {e}")
            raise
        finally:
            self.disconnect()

    def get_last_date_inventory(self) -> str:
        """
        Lấy date_time cuối cùng trong table inventory
        """
        try:
            self.connect()
            QUERY = f"SELECT date FROM {self.table} ORDER BY rowid DESC LIMIT 1;"
            last_date = pd.read_sql_query(QUERY, self.connection).iloc[0,0]
            logger.info(f"Last date inventory: {last_date}")
            return last_date
        except Exception as e:
            logger.error(f"Unexpected error during get data: {e}")
            raise
        finally:
            self.disconnect()
    
    def read_inventory_by_datetime(self, date_time: Optional[str]=None) -> pd.DataFrame:
        """
            Trả về Dataframe Inventory theo datetime
        Args:
            date_time or None
        Resuls:
            Nếu truyền data_time thì trả về date_time được truyền vào.
            Nếu không truyền date_time thì lấy date_time lần import gần nhất.
        """
        try:
            if not date_time:
                last_datetime = self.get_last_date_inventory()
            else:
                last_datetime = date_time

            self.connect()
            QUERY = f"SELECT * FROM {self.table} WHERE date = '{last_datetime}';"
            df = pd.read_sql_query(QUERY, self.connection)
            logger.info(f"Retrieved {len(df)} inventory records from database")
            return df
        except Exception as e:
            logger.error(f"Unexpected error during get data: {e}")
            raise
        finally:
            self.disconnect()

    def check_table_exists(self):
        """Check 1 table có tồn tại trong database không"""
        try:
            self.connect()
            query = f"""
            SELECT name
            FROM sqlite_master 
            WHERE type='table' AND name='{self.table}'
            """
            RESULS_CHECK = False
            result = self.connection.execute(text(query)).fetchone()
            if result:
                RESULS_CHECK = True
            else:
                RESULS_CHECK = False
            logger.info(f"Check exists table {self.table}: {RESULS_CHECK} ")
            return RESULS_CHECK
        except Exception as e:
            logger.error(f"Error check exists table: {e}")
            raise
        finally:
            self.disconnect()
