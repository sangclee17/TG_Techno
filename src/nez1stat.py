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

class NEZ1STAT():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
        self.SHU1NEZ = "PreModel_Shu1.NEZ"

    def process(self, anlsType, nezNm, savedModel_dir, condDict):
        # Create Modelinfo file using nez result files from 1st EPPS run
        if not self.fileExists(nezNm): return 0

        NEZ_STAT = {MAXDS:None, MINDS:None, AVGDS:None, REFP:None, 
                    MAXPL:None, MINPL:None, AVGPL:None, MINMT:None, 
                    MINPOSDS:None, MINPOSMT:None}

        self.Logger.info("Stats...Getting thickness result from {}".format(nezNm))
        modelInfo = {}
        refPoint = False
        if anlsType == "7":
            currentDict = {}
            coeff = 1e-6

            currentValueHozo = float(condDict["A021"])
            target_thickness = float(condDict["A026"])

            modelInfo_Hozo = _parsingNEZ(nezNm)
            if not self.fileExists(self.SHU1NEZ): return 0
            modelInfo_Shu = _parsingNEZ(self.SHU1NEZ)

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
                     
            # # put together Shu and Hozo
            # for key1 in modelInfo_Shu:
            #     if key1 in modelInfo_Hozo:
            #         if key1 in dsNodes or key1 in plNodes:
            #             modelInfo[key1] = modelInfo_Shu[key1] + modelInfo_Hozo[key1]            
            
            # hozoMax, hozoMin = _getMinMax(modelInfo)
            # NEZ_STAT[MAXMT] = hozoMax
            # NEZ_STAT[MINMT] = hozoMin

            # if hozoMin[1] < 0:
            #     hozoMin = _getMinMax(modelInfo, positiveOnly=True)
            #     NEZ_STAT[MINPOSMT] = hozoMin

            # # Comment out later    
            # with open("shuHozo_stat.txt", "w") as f:
            #     for key in modelInfo:
            #         f.write("{}:{}\n".format(key, modelInfo[key]))
            
            # # comment out later
            # with open("stats_hozo.txt", "w") as f:
            #     for key in NEZ_STAT:
            #         f.write("{}:{}\n".format(key,NEZ_STAT[key]))

            return NEZ_STAT

        elif anlsType == "2":
            refPoint = True

        modelInfo = _parsingNEZ(nezNm)

        self.Logger.info("Retrieve DS and PL node set Ids from {}".format(savedModel_dir))
        
        nodeSets = _getNodeSetEntities(savedModel_dir)

        if not nodeSets:
            self.Logger.error("Empty Node Sets in PreModels.slb")
            return 0

        modelInfo_DS = {}
        modelInfo_PL = {}

        dsNodes, plNodes = nodeSets

        for thisNode in plNodes:
            nodId = int(thisNode)
            if nodId in modelInfo:
                modelInfo_PL[nodId] = modelInfo[nodId]
        
        # # comment out later
        # with open("plNodes.txt", "w") as f:
        #     f.write("Total Length is {}\n".format(len(modelInfo_PL)))
        #     for key in modelInfo_PL:
        #         f.write("{}:{}\n".format(key, modelInfo_PL[key]))
        
        for thisNode in dsNodes:
            nodId = int(thisNode)
            if nodId in modelInfo:
                modelInfo_DS[nodId] = modelInfo[nodId]
        
        # # comment out later
        # with open("dsNodes.txt", "w") as f:
        #     f.write("Total Length is {}\n".format(len(modelInfo_DS)))
        #     for key in modelInfo_DS:
        #         f.write("{}:{}\n".format(key, modelInfo_DS[key]))
  
        self.Logger.info("Calculate the stack thickness corresponding to node ids")

        # Calculate statistics
        NEZ_STAT[AVGDS] = sum([modelInfo_DS[key] for key in modelInfo_DS])/ float(len(modelInfo_DS))
        NEZ_STAT[AVGPL] = sum([modelInfo_PL[key] for key in modelInfo_PL])/ float(len(modelInfo_PL))

        ds_max, ds_min = _getMinMax(modelInfo_DS)
        NEZ_STAT[MAXDS] = ds_max
        NEZ_STAT[MINDS] = ds_min

        if ds_min[1] < 0:
            ds_min = _getMinMax(modelInfo_DS, positiveOnly = True)
            NEZ_STAT[MINPOSDS] = ds_min

        pl_max, pl_min = _getMinMax(modelInfo_PL)
        NEZ_STAT[MAXPL] = pl_max
        NEZ_STAT[MINPL] = pl_min

        if refPoint:
            coord = condDict['A082']
            coord = coord.split(",")
            if len(coord) == 3:
                try:
                    x, y, z = float(coord[0]), float(coord[1]), float(coord[2])
                except ValueError:
                    self.Logger.error('Value Error, check "A082" from analysis conditions')
                    NEZ_STAT[REFP] = None
                else:
                    refNodId = int(self.findNearestNodeId(x, y, z))
                    NEZ_STAT[REFP] = modelInfo_DS[refNodId]
            else:
                self.Logger.error("Can't retrieve x, y, and z for reference point. Check 'A082' from analysis conditions")
                NEZ_STAT[REFP] = None

        # # comment out later
        # with open("stats.txt", "w") as f:
        #     for key in NEZ_STAT:
        #         f.write("{}:{}\n".format(key,NEZ_STAT[key]))
        
        return NEZ_STAT
    
    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.info("No such file or directory : {}".format(f_name))
            return False
        return True
    
    def findNearestNodeId(self, x, y, z, sphereRad = 1, increaseBy = 0.5):
        self.Logger.info("Finding the nearest node id from the given coordinates - X:{}, Y:{}, Z:{}".format(x,y,z))
        DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
        <tag Value="-1"/>
        <Name Value="Show_Nodes,"/>
        <Output/>
        </DeleteGroupControl>'''
        simlab.execute(DeleteGroupControl)

        # Select DS node face entities
        dsGroups = list(simlab.getGroupsWithSubString("FaceGroup",["*DSNodes"]))

        dsEnt = []
        for thisgrp in dsGroups:
            dsEnt.extend(list(simlab.getEntityFromGroup(thisgrp)))
        
        sphereCenter = "{},{},{}".format(x,y,z)
        
        while not simlab.isGroupPresent("Show_Nodes"):
            if sphereRad == 20: break
            self.Logger.info("Trying with the sphere radius {}".format(sphereRad))
            NodesByRegion=''' <NodesByRegion UUID="ad9db725-dcb3-4f9c-abd7-0e7a8cf64d05">
            <tag Value="-1"/>
            <Name Value="Show Nodes"/>
            <SupportEntities>
            <Entities>
            <Model>'''+ simlab.getModelName("FEM") +'''</Model>
            <Face>'''+ ",".join(str(v) for v in dsEnt) +''',</Face>
            </Entities>
            </SupportEntities>
            <Option Value="0"/>
            <RegionData Type="Sphere">
            <SphereData>
            <SphereCenter Value="'''+ sphereCenter +'''"/>
            <Radius Value="'''+ str(sphereRad) +'''"/>
            </SphereData>
            </RegionData>
            <On Value="0"/>
            <Above Value="0"/>
            <Below Value="1"/>
            <Tolerance Value="0"/>
            <MaximumCount Value="5000"/>
            <ShowSurfaceNodes Value="1"/>
            <CreateGroup Value="1"/>
            </NodesByRegion>'''
            simlab.execute(NodesByRegion)
            sphereRad += increaseBy
        
        nodeId = simlab.getEntityFromGroup("Show_Nodes")[0] if simlab.isGroupPresent("Show_Nodes") else None
        self.Logger.info("The nearest node id was found - nodeId: {}".format(nodeId))

        return nodeId

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

# current density vector
# X-curr.density
# Y-curr.density
# Z-curr.density
# voltage distribution
# stack thickness
# X-dir.stack
# Y-dir.stack
# Z-dir.stack
# overvoltage
# ratio of alloy #1
# ratio of alloy #2
# total current
# new position
# X-new position
# Y-new position
# Z-new position