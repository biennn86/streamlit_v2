from controllers.AnalysisControl import AnalysisControl

class DashBoardView:
    def __init__(self):
        self.analysiscontrol = AnalysisControl()
    def showlocation(self):
        return self.analysiscontrol.showtest()