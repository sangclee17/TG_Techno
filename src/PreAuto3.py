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
from nez2stat import NEZ2STAT
import sys_utility
import tg_utility

class TG():
    def __init__(self, folderNm, cond_dict):
        # WORKING DIR
        self.ANALYSISCONDITION = cond_dict
        self.SAVE_MODEL = "PreModel.slb"

        self.nez2stat = NEZ2STAT(None, "{}_log.txt".format(folderNm))
        self.neu2writer = NEU2Writer(None, "{}_log.txt".format(folderNm))
        self.neu2writer.Logger.info("######## Start PreAuto3 ########")

        self.HOZO1NEU = "PreModel_Hozo1.neu"
        self.HOZO1NEZ = "PreModel_Hozo1.NEZ"

        self.NEZ2MAIN = "PreModel2.NEZ"
        self.NEZ2HOZO = "PreModel2_hojyo.NEZ"
        self.NEZ2BACK = "PreModel2_rimen.NEZ"

        self.NEU3HOZO = "PreModel3_hojyo.neu"

        self.NEZ3MAIN = "PreModel3.NEZ"
        self.NEZ3HOZO = "PreModel3_hojyo.NEZ"
        self.NEZ3BACK = "PreModel3_rimen.NEZ"

        self.NEWINPUTCURRENT = "newInputCurrent.txt"       

    def createNeu3(self):
        shuType, hozoType, backType = self.ANALYSISCONDITION["A020"], self.ANALYSISCONDITION["A022"], self.ANALYSISCONDITION["A024"]
        shuVal = ""
        hojyoVal = ""
        rimenVal = ""

        if hozoType == '7' and shuType != "1":
            self.neu2writer.Logger.info("The given analysis case - Shu:{}, Hojyo:{}, Rimen:{}".format(shuType, hozoType, backType))
            self.neu2writer.Logger.info("Creating 3rd NEU input files...")
            hozoDictFromNez1 = self.nez2stat.process(self.HOZO1NEZ, self.SAVE_MODEL, self.ANALYSISCONDITION)
            newVal = self.neu2writer.getNewCurrentValForHozo(hozoType, self.ANALYSISCONDITION, hozoDictFromNez1)
            hojyoVal = newVal
            self.neu2writer.toFile(self.HOZO1NEU, self.NEU3HOZO, self.ANALYSISCONDITION, newVal)
            self.neu2writer.createinputFileText(self.NEU3HOZO)
            with open(self.NEWINPUTCURRENT, "r") as f:
                for line in f:
                    spline = line.rstrip().split(",")
                    shuVal = spline[0]
                    rimenVal = spline[2]
            self.neu2writer.exportNewInputCurrent(self.NEWINPUTCURRENT, shuVal, hojyoVal, rimenVal)

        nezFiles = [v for v in os.listdir() if v.endswith(".NEZ")]
        if self.NEZ2MAIN in nezFiles:
            self.neu2writer.toFile(self.NEZ2MAIN, self.NEZ3MAIN, self.ANALYSISCONDITION, "RENAME")
        if self.NEZ2HOZO in nezFiles:
            self.neu2writer.toFile(self.NEZ2HOZO, self.NEZ3HOZO, self.ANALYSISCONDITION, "RENAME")
        if self.NEZ2BACK in nezFiles:
            self.neu2writer.toFile(self.NEZ2BACK, self.NEZ3BACK, self.ANALYSISCONDITION, "RENAME")     
    
    def start(self):
        try:
            self.createNeu3()
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