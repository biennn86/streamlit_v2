from core.app_manager import AppManager

def get_state_everywhere():
    '''Helper function để lấy state từ bất kỳ đâu'''
    return AppManager().state

def reset_app_state():
    '''Helper function để reset toàn bộ state'''
    state = get_state_everywhere()
    state.clear()
    # Reinitialize with defaults
    from config.settings import AppConfig
    for key, value in AppConfig.DEFAULT_STATE.items():
        state[key] = value