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

    def create_table(self, create_table_sql) -> None:
        try:
            self.connect
            self.cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info(f"Table '{self.table}' created or confirmed existing")
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")
            raise
        except Exception as e:
            return None
        finally:
            self.disconnect()

    def insert_user(self, data) -> None:
        try:
            self.connect()
            columns = ', '.join(list(data.keys()))
            values = tuple(data.values())
            sql = "INSERT INTO {2}({0}) VALUES ({1})".format(columns, ', '.join(['%s'] * len(list(data.keys()))), self.table)
            self.cursor.execute(sql, values)
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error insert data to table {self.table}: {e}")
            raise
        except Exception as e:
            return None
        finally:
            self.disconnect()

    def update_user(self, username, data) -> None:
        try:
            self.connect()
            values = list(data.values())
            dataupdates = []
            for key in data.keys():
                dataupdates.append('{} = %s'.format(key))
            values.append(username)
            values = tuple(values)
            sql = "UPDATE {0} SET {1} WHERE username=%s".format(self.table, ', '.join(dataupdates))
            self.cursor.execute(sql, values)
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error update data to table {self.table}: {e}")
            raise
        except Exception as e:
            return None
        finally:
            self.disconnect()

    def delete_user(self, username) -> None:
        try:
            self.connect()
            sql = "DELETE FROM {0} WHERE username=%s".format(self.table)
            self.cursor.execute(sql, (username, ))
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Error delete data {self.table}: {e}")
            raise
        except Exception as e:
            return None
        finally:
            self.disconnect()
    
    def get_user_info(self, username) -> Dict[any, any]:
        try:
            self.connect()
            # sqlite3.Row là một lớp giống như tuple nhưng cho phép bạn truy cập các cột bằng cả chỉ mục (như tuple)
            # và tên cột (như dict)
            self.connection.row_factory = sqlite3.Row # Dòng code quan trọng
            self.cursor = self.connection.cursor()
            sql = "SELECT * FROM {0} WHERE username=%s".format(self.table)
            self.cursor.execute(sql, (username, ))
            
            result = self.cursor.fetchone()
            if result is None:
                return None
            return result
        except sqlite3.Error as e:
            logger.error(f"Error get data from table {self.table}: {e}")
            raise
        except Exception as e:
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
            # Drop the table if it exists and recreate it
            self.connect()
            self.cursor.execute(f"DROP TABLE IF EXISTS 'inventory'")
            self.disconnect()

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
