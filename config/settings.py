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
        StateKeys.FILE_UPLOADER: False
    }

    # App settings
    APP_TITLE = "MVC Streamlit App"
    APP_ICON = "🚀"
    LAYOUT = "wide"