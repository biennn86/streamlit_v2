from models.MergeDataModel import MergeDataModel

class MergeDataControl:
    def __init__(self):
        self.mergedata_model = MergeDataModel()
    def get_datamerge(self, df_inv):
        return self.mergedata_model.merge_inv_loc_masterdata(df_inv)