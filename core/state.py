import streamlit as st

class AppState:
    '''Quản lý trạng thái ứng dụng qua session_state với hỗ trợ dot notation'''
    def __init__(self, default_values=None):
        self._state = st.session_state
        if default_values:
            for key, value in default_values.items():
                if key not in self._state:
                    self._state[key] = value

    # -------- Dict-style access --------
    def get(self, key, default=None):
        return self._state.get(key, default)

    def set(self, key, value):
        self._state[key] = value

    def has(self, key):
        return key in self._state

    def remove(self, key):
        if key in self._state:
            del self._state[key]

    def clear(self):
        for key in list(self._state.keys()):
            del self._state[key]

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def __contains__(self, key):
        return key in self._state

    # -------- Dot notation access --------
    def __getattr__(self, name):
        if name in self._state:
            return self._state[name]
        raise AttributeError(f"'AppState' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        # Đảm bảo không ghi đè _state
        if name == "_state":
            super().__setattr__(name, value)
        else:
            self._state[name] = value

    def __delattr__(self, name):
        if name in self._state:
            del self._state[name]
        else:
            raise AttributeError(f"'AppState' object has no attribute '{name}'")