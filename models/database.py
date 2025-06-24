import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    ''' Quản lý kết nối và hoạt động của database '''
    __PATH_DB = "database/pg.db"
    def __init__(self):
        """Khỏi tạo quản lý database
        Args:
            None
        """
        self.table = None
        self.connection = None
        self.cursor = None
        self.df_import = None

    def connect(self) -> None:
        """Thiết lập kết nối tới database"""
        try:
            self.connection = sqlite3.connect(self.__PATH_DB)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database with table {self.table}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def disconnect(self) -> None:
        """Đóng kết nối tới database"""
        if self.connection:
            self.connection.close()
            logger.info(f"Database connection closed with table {self.table}")
            self.connection = None
            self.cursor = None
    
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
        except sqlite3.Error as e:
            logger.error(f"Error reading table: {e}")
            raise
        except Exception as e:
            return None
        finally:
            self.disconnect()

    def insert_dataframe(self, df: pd.DataFrame) -> None:
        """Insert a pandas DataFrame into a database table.
        
        Args:
            table_name: Name of the target table
            df: Pandas DataFrame containing the data to insert
        """
        try:
            # self.connect()
            # # Drop the table if it exists and recreate it
            # self.cursor.execute(f"DROP TABLE IF EXISTS 'inventory'")

            #chuyển toàn bộ df cần import sang string
            df = df.astype('string')
            # #lấy data đang có trong database
            df_old = self.read_to_dataframe()
            if df_old is not None:
                df_old = df_old.astype('string')
            # #Nối 2 dataframe. axis=0 là nối theo chiều dọc
            df_new = pd.concat([df_old, df], axis=0)
            # #lấy tổng số hàng bị trùng lặp trong df
            duplicates = df_new.duplicated().sum()

            self.connect()
            if (duplicates == 0):
                df.to_sql(self.table, self.connection, if_exists= 'append', index=False)
                logger.info(f"Inserted {len(df)} rows into table {self.table}")
                self.connection.commit()
            elif duplicates > 0:
                df_renew = pd.concat([df_new, df_old], axis=0).drop_duplicates(keep=False)
                df_renew.to_sql(self.table, self.connection, if_exists= 'append', index=False)
                self.connection.commit()
                logger.info(f"Inserted {len(df_renew)} rows into table {self.table}. Số dòng duplicates {duplicates}.")
            # self.conn.close() #6874, 6843
        except Exception as e:
            logger.error(f"Unexpected error during data insertion: {e}")
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
