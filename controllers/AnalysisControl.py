from models.MergeDataModel import MergeDataModel

class AnalysisControl:
    def __init__(self):
        self.mergedata = MergeDataModel()
    def showtest(self):
        return self.mergedata.merge_inv_loc_masdata()