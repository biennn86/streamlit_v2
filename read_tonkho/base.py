import sqlite3
import pandas as pd

class ConnectDB_2:
    __NAME_DB = 'D:/DATA/P&G/my_project/database/db_trans_rtcis.db'

    def getConection(self):
        try:
            self.conn = sqlite3.connect(self.__NAME_DB)
            return self.conn
        except:
            print('Connect Database Fail.')
    
    def get_df_from_db(table_name):
        with ConnectDB_2().getConection() as conn:
            QUERY = "SELECT * FROM {}".format(table_name)
            df = pd.read_sql_query(QUERY, conn)
            return df
    

