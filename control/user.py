from control.basecontrol import BaseControl

class User(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'master_user'