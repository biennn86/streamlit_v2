from abc import ABC, abstractmethod
from .state import AppState

class BaseController(ABC):
    '''Base controller với AppState tích hợp'''
    def __init__(self):
        # Khởi tạo state với các giá trị mặc định của app
        default_values = self.get_default_state()
        self.state = AppState(default_values)

    @abstractmethod
    def get_default_state(self):
        """Trả về dict các giá trị mặc định cho state"""
        return {}

    def reset_state(self):
        """Reset state về giá trị mặc định"""
        self.state.clear()
        default_values = self.get_default_state()
        for key, value in default_values.items():
            self.state[key] = value