from database.conect_db import ConnectDB
import pandas as pd

class BaseControl:
    def __init__(self):
        self.conn = ConnectDB().getConection()
        self.cursor = self.conn.cursor()
        self.table = None

    def insert(self, data):
        try:
            column_insert = ",".join(list(data.keys()))
            values_insert = tuple(data.values())
            sql = "INSERT INTO {2}({0}) VALUES ({1})".format(column_insert, ', '.join(['?'] * len(list(data.keys()))), self.table)
            self.cursor.execute(sql, values_insert)
            self.conn.commit()
        except:
            print("Insert Data Fail.")

    def get_df_from_db(self):
        try:
            with ConnectDB().getConection() as conn:
                QUERY = "SELECT * FROM {}".format(self.table)
                df = pd.read_sql_query(QUERY, conn)
                return df
        except:
            return None
        
    def insert_data_from_df(self, df: pd, method_insert = 'append'):
        try:
            with ConnectDB().getConection() as conn:
                df = df.astype('string')
                df_old = self.get_df_from_db()
                df_new = pd.concat([df_old, df], axis=0)
                duplicates = df_new.duplicated().sum()
                
                if duplicates == 0:
                    df.to_sql(self.table, conn, if_exists= method_insert, index=False)
                    print('Insert Data Vào Table {} Thành Công. Số Dòng Insert Được {}.'.format(self.table, len(df)))
                elif duplicates > 0:
                    df_renew = pd.concat([df_new, df_old], axis=0).drop_duplicates(keep=False)
                    df_renew.to_sql(self.table, conn, if_exists= method_insert, index=False)
                    print('Insert Data Vào Table {} Thành Công. Số Dòng Insert Được {}.'.format(self.table, len(df_renew)))
                # self.conn.close() #6874, 6843
        except:
            print("Insert Data From Datrframe Fail.")
            raise Exception
    
    def get_date_maxrowid(self):
        try:
            with ConnectDB().getConection() as conn:
                QUERY = "SELECT date FROM {} ORDER BY rowid DESC LIMIT 1;".format(self.table)
                last_date = pd.read_sql_query(QUERY, conn).iloc[0, 0]
                return last_date
        except:
            return None
        
    def get_all_inv(self):
        try:
            with ConnectDB().getConection() as conn:
                QUERY = "SELECT * FROM {};".format(self.table)
                data_inv = pd.read_sql_query(QUERY, conn)
                return data_inv
        except:
            return None
