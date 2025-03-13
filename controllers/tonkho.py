from controllers.BaseControl import BaseControl

class Inventory(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'inventory'