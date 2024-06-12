import os
import sys

# SRC DIR
SRC_DIR =  os.path.dirname(os.path.realpath(__file__))

# TG DIR
TG_DIR = os.path.abspath(os.path.join(SRC_DIR, os.pardir))

if not SRC_DIR in sys.path:
    sys.path.append(SRC_DIR)

# local import
from createInput import EPPS_Input
from createColorGrp import ColorGroup
import tg_utility
import sys_utility
import importlib

class TG():
    def __init__(self, folderNm, cond_dict):
        # WORKING DIR
        self.ANALYSISCONDITION = cond_dict
        self.SAVE_MODEL = "PreModel.slb"

        self.tg_util = tg_utility.TGUtility(None, "{}_log.txt".format(folderNm))
        self.tg_util.Logger.info("######## Start PreAuto1 ########")
        self.colorgrp = ColorGroup(None, "{}_log.txt".format(folderNm))
        self.eppsInput = EPPS_Input(None, "{}_log.txt".format(folderNm))

        self.EXPNEUName_SHU = "PreModel_Shu.neu"
        self.EXPFEMName_SHU = "PreModel_Shu.fem"
        self.EXPNEUName_BACK = "PreModel_Back.neu"
        self.EXPFEMName_BACK = "PreModel_Back.fem"
        self.EXPNEUName_HOZO = "PreModel_Hozo.neu"
        self.EXPFEMName_HOZO = "PreModel_Hozo.fem"
        self.COLOR_GRP_FILE = "groupsBycolors.xml"
        self.ANALYSIS_TYPE_HOZO = ["6","7"]
        self.ANALYSIS_TYPE_BACK = ["9"]

    def autoModeling(self):
        importlib.reload(tg_utility)
        try:
            restart = int(self.ANALYSISCONDITION["F006"])
        except KeyError as e:
            self.tg_util.error("No such paprameter, {}, from analysis conditions txt !!".format(e))
            return 0
        except ValueError:
            self.tg_util.error("Can't convert F006 to integer. Check analysis conditions txt !!")
            return 0

        if not restart:
            result = self.tg_util.getCadFile()
            if not result:return 0
            cadName, cadExt = result
            self.tg_util.importCad(cadName, cadExt)

            result = self.colorgrp.makeGrp(self.COLOR_GRP_FILE, self.ANALYSISCONDITION)
            if not result: return 0
            result = self.tg_util.importColorGrpSpec(self.COLOR_GRP_FILE)
            if not result: return 0

            # Create Simlab parameters
            result = self.tg_util.createSLParams(self.ANALYSISCONDITION)
            if not result: return 0

            # Create Mesh Control
            result = self.tg_util.createMCForTub()
            if not result: return 0
            self.tg_util.createMCForTheRest()

            # Surface meshing and transfer Groups
            self.tg_util.surfaceMesh(os.path.join(SRC_DIR, "advMeshOption.csv"))
            result = self.tg_util.transferFaceGrps()
            if not result: return 0
            self.tg_util.mergeAllBodiesByName()

            # Remove all free edges by filling holes
            self.tg_util.removeFreeEdges()

             # Quality and intersection check
            self.tg_util.meshQualityCleanUp()
            self.tg_util.intersectionCheck()

            # Merge DS Faces
            self.tg_util.mergeAllDSFaces() # Green and white SM group Faces

            # Create DS Node groups
            self.tg_util.createPLDSNodeSets()
            self.tg_util.mergeAllBodiesByName(bodyNm="Seihin")

            self.tg_util.exportSlb("PreModel_surf.slb")
            
            # Volume Meshing
            self.tg_util.volumeMesh(os.path.join(SRC_DIR, "advMeshOption.csv"))
            self.tg_util.unmergeBody()
            self.tg_util.exportSlb(self.SAVE_MODEL)
        else:
            if not self.tg_util.fileExists(self.SAVE_MODEL): return 0
            self.tg_util.importSlb(self.SAVE_MODEL)

        backAnode, hozoAnode = self.tg_util.checkAnode()

        # Create cathode node/element sets
        self.tg_util.createCathodeNodeElemSets()

        # Create anode element sets and export fem and neu files
        shuType, hozoType, backType = self.ANALYSISCONDITION["A020"], self.ANALYSISCONDITION["A022"], self.ANALYSISCONDITION["A024"]

        self.tg_util.Logger.info("The given analysis case: main - {}, hojyo - {}, rimen - {}".format(shuType, hozoType, backType))
        # Main analysis
        self.tg_util.exportFEMNEU("Shu", self.EXPFEMName_SHU, self.EXPNEUName_SHU)
        self.tg_util.exportSlb("PreModel_Shu.slb")

        # Rimen analysis
        if backAnode and (backType in self.ANALYSIS_TYPE_BACK):
            self.tg_util.exportFEMNEU("Back", self.EXPFEMName_BACK, self.EXPNEUName_BACK)
            self.tg_util.exportSlb("PreModel_Back.slb")

        # Hozo anlysis
        if hozoAnode and (hozoType in self.ANALYSIS_TYPE_HOZO):
            self.tg_util.exportFEMNEU("Hozo", self.EXPFEMName_HOZO, self.EXPNEUName_HOZO, self.SAVE_MODEL)
            self.tg_util.exportSlb("PreModel_hozo.slb")
        return 1
    
    def start(self):
        try:
            result = self.autoModeling()
            if not result:return 0

            # Create PreModel_??1.neu (input files)
            result = self.eppsInput.create(self.ANALYSISCONDITION)
            if not result:return 0

            return result

        except Exception as e:
            self.tg_util.Logger.error(e)
            return 0

def main(working_dir):
    print('working_dir=',working_dir)
    folderNm = os.path.basename(working_dir)
    sys_util = sys_utility.Sys_Utility(None, os.path.join(working_dir, "{}_log.txt".format(folderNm)))
    cond_dir = os.path.join(working_dir, "analysis_conditions.txt")
    if not sys_util.fileExists(cond_dir):return
    cond_dict = sys_util.readAnalysisCondition(cond_dir)

    # Move to working dir
    os.chdir(working_dir)

    # Instantiate TG
    tg = TG(folderNm, cond_dict)

    result = tg.start()
    if result:sys_util.exportKomPath(cond_dict)

if __name__ == "__main__":
    main(sys.argv[6])

    tg_utility.quitProgram()