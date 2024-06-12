import os
import sys

# SRC DIR
SRC_DIR =  os.path.dirname(os.path.realpath(__file__))

# TG DIR
TG_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))

# Proj Dir
PROJ_DIR = os.path.join(TG_DIR, "project")
CONFIG = os.path.join(PROJ_DIR, "sys_config.csv")

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

# local import
from create2ndInput import NEU2Writer
from nez1stat import NEZ1STAT
import sys_utility
import tg_utility

class TG():
    def __init__(self, folderNm, cond_dict):
        # WORKING DIR
        self.ANALYSISCONDITION = cond_dict
        self.SAVE_MODEL = "PreModel.slb"

        self.nez1stat = NEZ1STAT(None, "{}_log.txt".format(folderNm))
        self.neu2writer = NEU2Writer(None, "{}_log.txt".format(folderNm))
        self.neu2writer.Logger.info("######## Start PreAuto2 ########")

        self.SHU1NEU = "PreModel_Shu1.neu"
        self.HOZO1NEU = "PreModel_Hozo1.neu"

        self.SHU1NEZ = "PreModel_Shu1.NEZ"
        self.BACK1NEZ = "PreModel_Back1.NEZ"
        self.HOZO1NEZ = "PreModel_Hozo1.NEZ"

        self.NEU2_MAIN_INPUT = "PreModel2.neu"
        self.NEU2_HOZO_INPUT = "PreModel2_hojyo.neu"

        self.NEZ2MAIN = "PreModel2.NEZ"
        self.NEZ2HOZO = "PreModel2_hojyo.NEZ"
        self.NEZ2BACK = "PreModel2_rimen.NEZ"
        self.NEWINPUTCURRENT = "newInputCurrent.txt"       

    def createNeu2(self):
        self.neu2writer.Logger.info("Creating 2nd NEU input files...")
        shuType, hozoType, backType = self.ANALYSISCONDITION["A020"], self.ANALYSISCONDITION["A022"], self.ANALYSISCONDITION["A024"]
        self.neu2writer.Logger.info("The given analysis case - Shu:{}, Hojyo:{}, Rimen:{}".format(shuType, hozoType, backType))

        # Check first nez files
        nez1Files = [v for v in os.listdir() if v.endswith(".NEZ")]
        if not nez1Files:
            self.neu2writer.Logger.error("Failed EPPS server. Re-check mesh parameters, C001-D006 from analysis conditions txt")
            return 0
        shuVal = ""
        hojyoVal = ""
        rimenVal = ""
        self.neu2writer.Logger.info("Found NEZ files...{}".format(nez1Files))
        if self.HOZO1NEZ in nez1Files:
            self.neu2writer.Logger.info("Processing {}...".format(self.HOZO1NEZ))
            if hozoType == "6":
                hojyoVal = self.ANALYSISCONDITION["A021"]
                self.neu2writer.toFile(self.HOZO1NEZ, self.NEZ2HOZO, self.ANALYSISCONDITION, "RENAME")
            elif hozoType == "7" and shuType == "1":
                hozoDictFromNez1 = self.nez1stat.process(hozoType, self.HOZO1NEZ, self.SAVE_MODEL, self.ANALYSISCONDITION)
                newVal = self.neu2writer.getNewCurrentValForHozo(hozoType, self.ANALYSISCONDITION, hozoDictFromNez1)
                hojyoVal = newVal
                if not newVal:return 0
                if not self.neu2writer.fileExists(self.HOZO1NEU): return 0
                self.neu2writer.toFile(self.HOZO1NEU, self.NEU2_HOZO_INPUT, self.ANALYSISCONDITION, newVal)
                self.neu2writer.createinputFileText(self.NEU2_HOZO_INPUT)
        
        if self.SHU1NEZ in nez1Files:
            self.neu2writer.Logger.info("Processing {}...".format(self.SHU1NEZ))
            if shuType == "1":
                shuVal = self.ANALYSISCONDITION['A019']
                self.neu2writer.toFile(self.SHU1NEZ, self.NEZ2MAIN, self.ANALYSISCONDITION, "RENAME")
            elif shuType in ["2", "3", "4", "5"]:
                shuDictFromNez1 = self.nez1stat.process(shuType, self.SHU1NEZ, self.SAVE_MODEL, self.ANALYSISCONDITION)
                newVal = self.neu2writer.getNewCurrentValForShu(shuType.strip(), self.ANALYSISCONDITION, shuDictFromNez1)
                shuVal = newVal
                if not newVal:return 0
                if not self.neu2writer.fileExists(self.SHU1NEU):return 0
                self.neu2writer.toFile(self.SHU1NEU, self.NEU2_MAIN_INPUT, self.ANALYSISCONDITION, newVal)
                self.neu2writer.createinputFileText(self.NEU2_MAIN_INPUT)
                    
        if self.BACK1NEZ in nez1Files:
            self.neu2writer.Logger.info("Processing {}...".format(self.BACK1NEZ))
            if backType.strip() == "9":
                rimenVal = self.ANALYSISCONDITION["A023"]
                self.neu2writer.toFile(self.BACK1NEZ, self.NEZ2BACK, self.ANALYSISCONDITION, "RENAME")
        
        self.neu2writer.exportNewInputCurrent(self.NEWINPUTCURRENT, shuVal, hojyoVal, rimenVal)
        return 1            
    
    def start(self):
        try:
            result = self.createNeu2()
            if not result:return
        except Exception as e:
            self.neu2writer.Logger.error(e)

def main(working_dir):
    folderNm = os.path.basename(working_dir)

    sys_util = sys_utility.Sys_Utility(None, os.path.join(working_dir, "{}_log.txt".format(folderNm)))
    cond_dir = os.path.join(working_dir, "analysis_conditions.txt")
    if not sys_util.fileExists(cond_dir):return
    cond_dict = sys_util.readAnalysisCondition(cond_dir)

    # Move to working dir
    os.chdir(working_dir)

    # Instantiate TG
    tg = TG(folderNm, cond_dict)

    tg.start()

if __name__ == "__main__":
    main(sys.argv[6])

    tg_utility.quitProgram()