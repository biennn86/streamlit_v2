import sqlite3

class ConnectDB:
    __NAME_DB = 'database\\pg.db'

    def getConection(self):
        try:
            self.conn = sqlite3.connect(self.__NAME_DB)
            print(f"Kết nối Database thành công.")
            return self.conn
        except Exception as e:
            print(f"Connect Database Fail. {e}")
