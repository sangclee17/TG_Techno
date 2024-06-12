import os
from hwx import simlab
from Logger import Logger

MAXDS = "MaxDS"
MINDS = "MinDS"
AVGDS = "AvgDS"
MAXMT = "MaxMt1DS"
MINMT = "MinMt1DS"
REFP = "B015DS"
MAXPL = "MaxPL"
MINPL = "MinPL"
AVGPL = "AvgPL"
MINPOSDS = "MinPosDS"
MINPOSMT = "MinMt1PosDS"

class NEZ2STAT():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
        self.SHU2NEZ = "PreModel2.nez"

    def process(self, nezNm, savedModel_dir, condDict):
        # Create Modelinfo file using nez result files from 1st EPPS run
        if not self.fileExists(nezNm): return 0

        NEZ_STAT = {MAXDS:None, MINDS:None, AVGDS:None, REFP:None, 
                    MAXPL:None, MINPL:None, AVGPL:None, MINMT:None, 
                    MINPOSDS:None, MINPOSMT:None}

        self.Logger.info("Stats...Getting thickness result from {}".format(nezNm))
        currentDict = {}
        coeff = 1e-6

        currentValueHozo = float(condDict["A021"])
        target_thickness = float(condDict["A026"])

        modelInfo_Hozo = _parsingNEZ(nezNm)
        if not self.fileExists(self.SHU2NEZ): return 0
        modelInfo_Shu = _parsingNEZ(self.SHU2NEZ)

        nodeSets = _getNodeSetEntities(savedModel_dir)
        dsNodes, plNodes = nodeSets

        for key1 in modelInfo_Shu:
            if key1 in modelInfo_Hozo:
                if key1 in dsNodes or key1 in plNodes:
                    thicknessDiff = target_thickness * coeff - modelInfo_Shu[key1]
                    currentAmp = thicknessDiff / modelInfo_Hozo[key1]
                    currentDict[key1] = currentAmp * currentValueHozo

        maxCurrent, _ = _getMinMax(currentDict)

        NEZ_STAT[MAXMT] = maxCurrent

        return NEZ_STAT
    
    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.info("No such file or directory : {}".format(f_name))
            return False
        return True

def _getMinMax(aDict, positiveOnly = False):
    if positiveOnly:
        aMin = min((a for a in aDict.items() if a[1]>0), key= lambda x: x[1])
        return aMin
    aMax = max(aDict.items(), key= lambda x: x[1])
    aMin = min(aDict.items(), key= lambda x: x[1])
    return aMax, aMin

def _parsingNEZ(nezPath):
    aDict = {}
    with open(nezPath, "r") as f:
        skipLine = True
        for line in f:
            line = line.rstrip()
            if "stack thickness" in line.lower():
                skipLine = False
                continue
            if not skipLine:
                lineSP = line.split(",")
                if line.startswith("-1"): break
                if not line.startswith("0") and len(lineSP)==3:
                    nodeId = int(lineSP[0])
                    thickness = float(lineSP[1])
                    aDict[nodeId] = thickness

    return aDict

def _getNodeSetEntities(slbPath):
    ImportSlb=''' <ImportSlb CheckBox="ON" UUID="C806F6DF-56FA-4134-9AD1-1010BF292183" gda="">
    <tag Value="1"/>
    <Name Value=""/>
    <FileName Value="'''+ slbPath +'''"/>
    <ImportOrOpen Value="0"/>
    <Output/>
    </ImportSlb>'''
    simlab.execute(ImportSlb)

    dsNodes = simlab.getEntitiesFromSet("All_DSNodes")
    plNodes = simlab.getEntitiesFromSet("All_PLNodes")
    if not dsNodes or not plNodes:
        return None
    else:
        return (dsNodes, plNodes)