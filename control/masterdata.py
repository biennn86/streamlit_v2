from control.basecontrol import BaseControl

class MasterData(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'master_data'