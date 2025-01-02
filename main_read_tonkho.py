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
        self.df_empty_loc = self.objTonkho.EmptyLoc()
        return self.df_empty_loc
    def combinebin(self):
        self.df_bincombine = self.objTonkho.CombineBin()
        return self.df_bincombine
    def binmixup(self):
        self.df_mixup = self.objTonkho.FindMixup()
        return self.df_mixup
    def get_inv(self):
        self.df_inventory = self.objTonkho.Get_Inventory()
        return self.df_inventory
    
class CreateLocMasterData:
    def CreateLocaion(self):
        main_createloc()

        
if __name__ == '__main__':
    # mainReadTonkho()
    main_createloc()