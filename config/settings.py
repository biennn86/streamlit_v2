class AppConfig:
    '''Cấu hình ứng dụng'''


    # State keys - tập trung quản lý tên các key
    class StateKeys:
        # User related
        IS_LOGGED_IN = 'is_logged_in'
        USERNAME = 'username'
        USER_ROLE = 'user_role'
        LOGIN_ATTEMPTS = 'login_attempts'

        # App related
        CURRENT_PAGE = 'current_page'
        THEME = 'theme'
        LANGUAGE = 'language'

        # Data related
        SELECTED_DATA = 'selected_data'
        FILTERS = 'filters'
        USER_PROFILE = 'user_profile'
        DASHBOARD_DATA = 'dashboard_data'
        FILE_UPLOADER = 'file_uploader'
        UPLOADER_ID = 'uploader_id'
        CURRENT_FILES = 'current_files '
        LAST_PROCESSED_FILES = 'last_processed_files'
        # Data bin to bin
        UPLOAD_ID_INV_BTB = "upload_id_inv_btb"
        UPLOAD_ID_DEMAND = "upload_id_demand"
        INV_BTB = "inv_btb"
        DEMAND_DATA = "demand_data"
        FILE_UPLOADER_INV_BTB = "file_uploader_inv_btb"
        FILE_UPLOADER_DEMAND = "file_uploader_demand"
        CURRENT_FILE_INV_BTB = "curren_file_inv_btb"
        CURRENT_FILE_DEMAND = "curren_file_demand"
        DF_BTB = "df_btb"
        STRATEGY_BTB = "strategy_btb"
        ITEM_NOT_BTB = "item_not_btb"

    # Default values
    DEFAULT_STATE = {
        StateKeys.IS_LOGGED_IN: False,
        StateKeys.USERNAME: '',
        StateKeys.USER_ROLE: 'guest',
        StateKeys.LOGIN_ATTEMPTS: 0,
        StateKeys.CURRENT_PAGE: 'login',
        StateKeys.THEME: 'light',
        StateKeys.LANGUAGE: 'vi',
        StateKeys.SELECTED_DATA: None,
        StateKeys.FILTERS: {},
        StateKeys.USER_PROFILE: {},
        StateKeys.DASHBOARD_DATA: {},
        StateKeys.FILE_UPLOADER: False,
        StateKeys.UPLOADER_ID: 0,
        StateKeys.CURRENT_FILES: [],
        StateKeys.LAST_PROCESSED_FILES: [],
        # btb
        StateKeys.UPLOAD_ID_INV_BTB: 0,
        StateKeys.UPLOAD_ID_DEMAND: 0,
        StateKeys.INV_BTB: None,
        StateKeys.DEMAND_DATA: {},
        StateKeys.FILE_UPLOADER_INV_BTB: False,
        StateKeys.FILE_UPLOADER_DEMAND: False,
        StateKeys.CURRENT_FILE_INV_BTB: [],
        StateKeys.CURRENT_FILE_DEMAND: [],
        StateKeys.DF_BTB: None,
        StateKeys.STRATEGY_BTB: "standard",
        StateKeys.ITEM_NOT_BTB: [],
    }

    # App settings
    APP_TITLE = "MVC Streamlit App"
    APP_ICON = "🚀"
    LAYOUT = "wide"