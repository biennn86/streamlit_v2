from typing import List, Tuple, Dict, Any, Optional
from core.base_state_controller import BaseStateController
from models.user_model import UserModel
from config.settings import AppConfig

class UserController(BaseStateController):
    '''Controller xử lý logic người dùng'''
    def __init__(self):
        super().__init__()
        self.user_model = UserModel()

    def get_default_state(self) -> Dict:
        """Giá trị mặc định cho user state"""
        return {
            AppConfig.StateKeys.IS_LOGGED_IN: False,
            AppConfig.StateKeys.USERNAME: '',
            AppConfig.StateKeys.USER_ROLE: 'guest',
            AppConfig.StateKeys.LOGIN_ATTEMPTS: 0,
            AppConfig.StateKeys.USER_PROFILE: {}
        }
    
    def login(self, username, password) -> bool:
        """Xử lý đăng nhập"""
        if self.user_model.validate_credentials(username, password):
            #Update ngày giờ last_login
            self.user_model.update_last_login(username=username)
            #Update trạng thái online
            self.user_model.update_is_online(username=username)
            #Lấy data user trong database
            user_info = self.user_model.get_user_info(username)

            # Cập nhật state
            self.state.is_logged_in = True
            self.state.username = username
            self.state.user_role = user_info["role"]
            self.state.login_attempts = 0
            self.state.user_profile = user_info
            self.state.current_page = "dashboard"

            return True
        else:
            self.state.login_attempts += 1
            return False

    def logout(self) -> None:
        """Xử lý đăng xuất"""
        #update trạng thái offline
        self.user_model.update_is_offline(username=self.state.get(AppConfig.StateKeys.USERNAME, False))
        #xử lý state logout
        self.state.is_logged_in = False
        self.state.username = ''
        self.state.user_role = 'guest'
        self.state.user_profile = {}
        self.state.current_page = 'login'

    def is_authenticated(self) -> bool:
        """Kiểm tra trạng thái đăng nhập"""
        return self.state.get(AppConfig.StateKeys.IS_LOGGED_IN, False)

    def has_role(self, required_role) -> bool:
        """Kiểm tra quyền user"""
        user_role = self.state.get(AppConfig.StateKeys.USER_ROLE, 'guest')
        role_hierarchy = {'guest': 0, 'demo': 1, 'user': 2, 'admin': 3}
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

    def update_profile(self, profile_data) -> bool:
        """Cập nhật thông tin profile"""
        username = self.state.username
        if self.user_model.update_user_profile(username, profile_data):
            # Cập nhật state
            # self.state.user_profile.update(profile_data)
            self.state.user_profile = profile_data
            return True
        return False
    
    def register_user(self, profile_user) -> bool:
        """Đăng ký user mới"""
        if self.user_model.insert_user(profile_user):
            return True
        return False

    def get_login_attempts(self) -> int:
        """Lấy số lần đăng nhập thất bại"""
        return self.state.get(AppConfig.StateKeys.LOGIN_ATTEMPTS, 0)