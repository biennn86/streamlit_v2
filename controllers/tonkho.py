from control.basecontrol import BaseControl

class Inventory(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'inventory'