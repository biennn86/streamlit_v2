from models.database_model import DatabaseManager

class TableNameInventory(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "inventory"
        if not self.check_table_exists():
            self._create_table_inventory()
            self.ensure_indexes()
    
    def _create_table_inventory(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            date        DATETIME,
            gcas        INTEGER,
            batch       TEXT,
            vnl         TEXT,
            status      TEXT,
            qty         REAL,
            pallet      INTEGER,
            location    TEXT,
            note_inv    TEXT,
            cat_inv     TEXT,
            created_at  DATETIME,
            user        TEXT
        );
        """
        return self.create_table(create_table_sql)

    def ensure_indexes(self):
        key_columns = ['date', 'gcas', 'location']
        self.create_indexes(key_columns=key_columns)
        


class TableNameMasterdata(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "master_data"
        if not self.check_table_exists():
            self._create_table_masterdata()
            self.ensure_indexes()

    def _create_table_masterdata(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            gcas                   INTEGER,
            description            TEXT,
            cat                    TEXT,
            type1                  TEXT,
            type2                  TEXT,
            vendor_name            TEXT,
            source                 TEXT,
            jit                    TEXT,
            bd_plt_pat             TEXT,
            history_storeLocation  TEXT,
            latest_gr              TEXT,
            created_at             DATETIME,
            user                   TEXT
        );
        """

        return self.create_table(create_table_sql)

    def ensure_indexes(self):
        key_columns = ['gcas', 'bd_plt_pat']
        self.create_indexes(key_columns=key_columns)
        
class TableNameLocation(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "master_location"
        if not self.check_table_exists():
            self._create_table_location()
            self.ensure_indexes()

    def _create_table_location(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            location                   TEXT,
            location_system_type       TEXT,
            location_usage_type        TEXT,
            rack_system_type           TEXT,
            rack_usage_type            TEXT,
            location_storage_type      TEXT,
            zone                       TEXT,
            location_category          TEXT,
            location_product_category  TEXT,
            name_rack                  TEXT,
            bayslot                    INTEGER,
            level                      TEXT,
            location_hight             TEXT,
            name_warehouse             TEXT,
            pallet_capacity            INTEGER,
            stack_limit                INTEGER,
            foot_print                 INTEGER,
            is_active                  INTEGER,
            status_location            TEXT,
            note                       TEXT,
            created_at                 DATETIME,
            user                       TEXT
        );
        """
    # def _create_table_location(self):
    #     create_table_sql = f"""
    #     CREATE TABLE IF NOT EXISTS {self.table} (
    #         location        TEXT,
    #         type_rack       TEXT,
    #         cat_rack        TEXT,
    #         type_loc        TEXT,
    #         name_wh         TEXT,
    #         name_rack       TEXT,
    #         level           TEXT,
    #         num_pallet      INTEGER,
    #         stack_limit     TEXT,
    #         foot_print      INTEGER,
    #         note            TEXT,
    #         created_at      DATETIME,
    #         user            TEXT
    #     );
    #     """
        return self.create_table(create_table_sql)

    def ensure_indexes(self):
        key_columns = ['location']
        self.create_indexes(key_columns=key_columns)

class TableNameUser(DatabaseManager):
    def __init__(self):
        super().__init__()
        self.table = "user"
        if not self.check_table_exists():
            from models.user_model import UserModel
            self._create_table_user()
            self.user_mode = UserModel()
            self.create_default()

    def _create_table_user(self) -> None:
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
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
        
        return self.create_table(create_table_sql)

    def create_default(self):
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
        self.user_mode.insert_user(create_user_admin)

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
        self.user_mode.insert_user(create_user_edit)

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
        self.user_mode.insert_user(create_user_view)

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
        self.user_mode.insert_user(create_user_demo)
