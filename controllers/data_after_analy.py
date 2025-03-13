from control.basecontrol import BaseControl

class DataAnalys(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'data_after_analysis'