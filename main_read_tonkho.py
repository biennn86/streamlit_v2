from read_tonkho.read_rpm import *
from create_location.create_loc import *
from read_tonkho.readInvFromDB import *
from dashboard.dashboardTonkho import *

class BackEndSteamLit:
    def __init__(self, data_uploaded):
        self.data_uploaded = data_uploaded
        self.objTonkho = CreateDfToDB(self.data_uploaded)
        # self.objTonkho.EmptyLoc()
        # self.objTonkho.FindMixup()
        # self.objTonkho.CombineBin()

    def mainReadTonkho(self):
        dfDataFinal = self.objTonkho.MergeTonkhoMtdataMtLoc()
        return dfDataFinal
        # objSumaryPlWh = SummaryPalletWhithWh(dictData)
        # print(objSumaryPlWh.dictNameWh['wh3'].hr_rpm)
    # def GetEMptyLoc(self):
    #     return self.objTonkho.EmptyLoc()
    def emptyloc(self):
        emp = self.objTonkho.EmptyLoc()
        return emp
    def combinebin(self):
        bincombine = self.objTonkho.CombineBin()
        return bincombine
    def binmixup(self):
        mixup = self.objTonkho.FindMixup()
        return mixup
class CreateLocMasterData:
    def CreateLocaion(self):
        main_createloc()

        
if __name__ == '__main__':
    # mainReadTonkho()
    main_createloc()