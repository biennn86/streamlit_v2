from controllers.MergeDataControl import MergeDataControl
from views.Tabs import Tabs

class MergeDataView:
    def __init__(self):
        self.mergedatacontrol = MergeDataControl()
    def render_mergedata(self, df_inv):
        data_merge =  self.mergedatacontrol.get_datamerge(df_inv)
        Tabs().tab_dashboard(data_merge)
        return data_merge