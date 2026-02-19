from controllers.BaseControl import BaseControl

class LocationNew(BaseControl):
    def __init__(self):
        super().__init__()
        self.table = 'master_location_new'