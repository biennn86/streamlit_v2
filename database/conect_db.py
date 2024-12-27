import sqlite3

class ConnectDB:
    __NAME_DB = 'database\\pg.db'

    def getConection(self):
        try:
            self.conn = sqlite3.connect(self.__NAME_DB)
            print("kết nối db thành công")
            return self.conn
        except:
            print('Connect Database Fail.')
