from models.masterdata import MasterdataModel

class MasterdataController:
    def __init__(self):
        self.masterdata_model = MasterdataModel()
    def import_masterdata(self, link_file: str):
        self.masterdata_model.process_file_masterdata(link_file)