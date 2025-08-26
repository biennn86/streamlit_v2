from .state import AppState
from config.settings import AppConfig

class AppManager:
    '''Singleton để quản lý state toàn cục'''
    _instance = None
    _state = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._state = AppState(AppConfig.DEFAULT_STATE)
        return cls._instance

    @property
    def state(self):
        return self._state

    def get_controller(self, controller_class):
        """Factory method để tạo controller với state chung"""
        controller = controller_class()
        controller.state = self._state  # Chia sẻ state
        return controller