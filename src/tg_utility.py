import os
import shutil
import csv
from hwx import simlab
from datetime import datetime
from Logger import  Logger

class TGUtility():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
        self.INTERSECTION_GROUP = "Intersect_Elems"

    def updateFolderNms(self, wFolderNm, folderNmDir):
        folderNms = []
        with open(folderNmDir, 'r') as f:
            for line in f.readlines():
                folderNm = line.strip("\n")
                if folderNm != wFolderNm:
                    folderNms.append()

        writeToFile(folderNmDir,"w",folderNms)
    
    def getCadFile(self):
        cadFile = [f for f in os.listdir() if f.endswith(".stp") or f.endswith(".step") or f.endswith(".CATPart")]
        if not cadFile:
            self.Logger.error("Can't find a cad file in .stp, .step, or .CATPart")
            return False
        cadName = cadFile[0]
        cadExt = cadName.split(".")[1]
        
        return (cadName, cadExt)

    def createSLParams(self, md):
        self.Logger.info("Creating SimLab parameters...")
        try:
            createParam("real","MainMeshSize", float(md["C001"]))
            createParam("real","MinMainMeshSize", float(md["C002"]))
            createParam("real","MainGradeFactor", float(md["C003"]))
            createParam("real","MainFeatureAngle", float(md["C004"]))
            createParam("real","MainCurvMinSize", float(md["C005"]))
            createParam("real","MainAspectRatio", float(md["C006"]))
            createParam("real","TubMeshSize", float(md["C007"]))
            createParam("real","MinTubMeshSize", float(md["C008"]))
            createParam("real","TubGradeFactor", float(md["C009"]))
            createParam("real","TubFeatureAngle", float(md["C010"]))
            createParam("real","TubGradeFactorCurvMinSize", float(md["C011"]))
            createParam("real","TubAspectRatio", float(md["C012"]))
            createParam("real","TetElemSize", float(md["C013"]))
            createParam("real","TetGradeFactor", float(md["C014"]))
            createParam("real","TetMinSize", float(md["C015"]))
            createParam("string","AnodeProp", md["D001"])
            createParam("int","AnodePID", int(md["D002"]))
            createParam("string","CathodeProp", md["D003"])
            createParam("int","CathodePID", int(md["D004"]))
            createParam("string","MekkiekiProp", md["D005"])
            createParam("int","MekkiekiPID", int(md["D006"]))
        except KeyError as e:
            self.Logger.error("No such paprameter, {} from analysis conditions txt !!".format(e))
            return 0
        return 1

    def importCad(self, cadNm, cadExt):
        self.Logger.info("Importing {}".format(cadNm))
        if cadExt == "CATPart":
            ImportCatia=''' <ImportCatia CheckBox="ON" UUID="81027e04-fb12-4eac-a5d1-cc1880a5bb7d" gda="">
            <tag Value="1"/>
            <Method Value="2"/>
            <Name Value=""/>
            <FileName Value="'''+ cadNm +'''"/>
            <Units Value="MilliMeter"/>
            <DesignParam Value="0"/>
            <Datum Value="0"/>
            <BodyName Value="1"/>
            <UsePartNameForFilesWithOneBody Value="0"/>
            <Color Value="1"/>
            <Publications Value="0"/>
            <Skethch Value="0"/>
            <Coordinates Value="0"/>
            <IncludeFiles Value="0"/>
            <Sheet Value="0"/>
            <Regenerate Value="0"/>
            <RegenModelId Value="0"/>
            <ImportAsFacets Value="0"/>
            <ImportAsmStruct Value="0"/>
            <IncludeFileNameList Value=""/>
            <Output/>
            </ImportCatia>'''
            simlab.execute(ImportCatia)

        elif (cadExt == "stp") or (cadExt == "step"):
            ImportStep='''<ImportStep CheckBox="ON" UUID="4d0e7cd9-d1a5-4c1d-98e4-1efcf652facb" gda="">
            <tag Value="1"/>
            <Name Value=""/>
            <FileName Value="'''+ cadNm +'''"/>
            <BodyName Value="1"/>
            <FaceColor Value="1"/>
            <ImportAsFacets Value="0"/>
            <ReadSketch Value="0"/>
            <Output/>
            </ImportStep>'''
            simlab.execute(ImportStep)

    def exportSlb(self, fName):
        self.Logger.info("Saving slb model in {}".format(fName))
        ExportSlb=''' <ExportSlb UUID="a155cd6e-8ae6-4720-8ab4-1f50d4a34d1c">
        <tag Value="-1"/>
        <Name Value=""/>
        <Option Value="1"/>
        <FileName Value="'''+ fName + '''"/>
        </ExportSlb>'''
        simlab.execute(ExportSlb)
    
    def importColorGrpSpec(self, fName):
        if not self.fileExists(fName): return 0
        self.Logger.info("Importing {}".format(fName))
        modelNm = simlab.getModelName('CAD')
        ImportSpecification='''<ImportSpecification UUID="bda28225-2d4d-4364-8f9e-9e0a440fb83c" pixmap="import">\
        <tag Value="-1"/>
        <Name Value="ImportSpecification3"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body></Body>
        </Entities>
        </SupportEntities>
        <FileName Value="'''+ fName +'''"/>
        <CurrentTab Value=""/>
        <Tolerance Value=""/>
        <ImportSpecType Value="-1"/>
        <Output/>
        </ImportSpecification>'''
        simlab.execute(ImportSpecification)
        grpNms = simlab.getGroupsWithSubString("FaceGroup",["*"])
        for this_grp in grpNms:
            grpEnts = simlab.getEntityFromGroup(this_grp)
            if not grpEnts:
                deleteGrp(this_grp)
        return 1
    
    def createMCForTub(self):
        self.Logger.info("Creating Body Mesh Control for Tub")
        tubBody = simlab.getBodiesWithSubString(simlab.getModelName("CAD"), ["Tub"])
        if not tubBody:
            self.Logger.error("Can't find the body named Tub")
            return 0
        modelNm = simlab.getModelName("CAD")
        MeshControls='''<MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">
        <tag Value="-1"/>
        <MeshControlName Value="MekkiSou"/>
        <MeshType Value="0"/>
        <Entities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body>"Tub",</Body>
        </Entities>
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value=""/>
        <BodyMeshControl>
        <ElementType Value="0"/>
        <UseMaxElemSize Value="0"/>
        <AverageElementSize Value="$TubMeshSize"/>
        <MaxElemSize Value="$TubMeshSize*1.414"/>
        <MinElemSize Value="$MinTubMeshSize"/>
        <MaxAnglePerElement Value="$TubFeatureAngle"/>
        <CurvatureMinElemSize Value="$TubGradeFactorCurvMinSize"/>
        <AspectRatio Value="$TubAspectRatio"/>
        <SurfaceMeshGrading Value="$TubGradeFactor"/>
        <MappedMesh Value="0"/>
        <CoarseMesh Value="0"/>
        <IdentifyFeaturesandMesh Value="0"/>
        </BodyMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)
        return 1

    def createMCForTheRest(self):
        bdyList = list(simlab.getBodiesWithSubString(simlab.getModelName("CAD"), ["*"]))
        bdyList.remove('Tub')
        self.Logger.info("Creating Body Mesh Control for the rest")

        modelNm = simlab.getModelName("CAD")
        MeshControls=''' <MeshControl CheckBox="ON" isObject="1" UUID="1cb8a11b-39b0-417e-80b5-fa99a34ce8d3">\
        <tag Value="-1"/>
        <MeshControlName Value="WorkYoukyokuInkyokuAntena"/>
        <MeshType Value="0"/>
        <Entities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body>'''+ ','.join('"{}"'.format(v) for v in bdyList) +''',</Body>
        </Entities>
        </Entities>
        <Reverse EntityTypes="" ModelIds="" Value=""/>
        <MeshColor Value=""/>
        <BodyMeshControl>
        <ElementType Value="0"/>
        <UseMaxElemSize Value="0"/>
        <AverageElementSize Value="$MainMeshSize"/>
        <MaxElemSize Value="$MainMeshSize*1.414"/>
        <MinElemSize Value="$MinMainMeshSize"/>
        <MaxAnglePerElement Value="$MainFeatureAngle"/>
        <CurvatureMinElemSize Value="$MainCurvMinSize"/>
        <AspectRatio Value="$MainAspectRatio"/>
        <SurfaceMeshGrading Value="$MainGradeFactor"/>
        <MappedMesh Value="0"/>
        <CoarseMesh Value="0"/>
        <IdentifyFeaturesandMesh Value="0"/>
        </BodyMeshControl>
        </MeshControl>'''
        simlab.execute(MeshControls)

    def surfaceMesh(self, optionCsv):
        self.Logger.info("2D Meshing...")

        advOption = {}
        with open(optionCsv, "r") as f:
            lines = f.readlines()
            for this_line in lines:
                if not this_line.startswith("#"):
                    spline = this_line.strip().split(",")
                    advOption[spline[0]] = spline[1]
                
        modelNm = simlab.getModelName("CAD")
        SurfaceMesh=''' <SurfaceMesh UUID="08df0ff6-f369-4003-956c-82781326c876">
        <tag Value="-1"/>
        <SurfaceMeshType Value="Tri"/>
        <SupportEntities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body></Body>
        </Entities>
        </SupportEntities>
        <Tri>
        <ElementType Value="Tri3"/>
        <AverageElementSize Checked="1" Value="$MainMeshSize"/>
        <MaximumElementSize Checked="0" Value="5.656"/>
        <MinimumElementSize Value="$MinMainMeshSize"/>
        <GradeFactor Value="$MainGradeFactor"/>
        <MaximumAnglePerElement Value="$MainFeatureAngle"/>
        <CurvatureMinimumElementSize Value="$MainCurvMinSize"/>
        <AspectRatio Value="$MainAspectRatio"/>
        <AdvancedOptions>
        <IdentifyFeaturesAndMesh Checked="'''+ advOption["IdentifyFeaturesAndMesh"] +'''"/>
        <ImprintMeshing Checked="'''+ advOption["ImprintMeshing"] +'''"/>
        <BetterGeometryApproximation Checked="'''+ advOption["BetterGeometryApproximation"] +'''"/>
        <CoarseMesh Checked="'''+ advOption["CoarseMesh"] +'''"/>
        <CoarseMesh_UseExistingNodes Checked="'''+ advOption["CoarseMesh_UseExistingNodes"] +'''"/>
        <CreateMeshInNewModel Checked="'''+ advOption["CreateMeshInNewModel"] +'''"/>
        <UserDefinedModelName Value="'''+ advOption["UserDefinedModelName"] +'''"/>
        <Tri6WithStraightEdges Checked="'''+ advOption["Tri6WithStraightEdges"] +'''"/>
        <ImproveSkewAngle Value="'''+ advOption["ImproveSkewAngle"] +'''"/>
        <MappedMesh Value="'''+ advOption["MappedMesh"] +'''"/>
        <MeshPattern Value="'''+ advOption["MeshPattern"] +'''"/>
        </AdvancedOptions>
        </Tri>
        </SurfaceMesh>'''
        simlab.execute(SurfaceMesh)

    def transferFaceGrps(self):
        self.Logger.info("Transfer groups from CAD to FEM")
        model1 = simlab.getModelName("CAD")
        model2 = simlab.getModelName("FEM")
        if model2 == "":
            self.Logger.error("Can't find the FEM model")
            return 0
        TransferGroup=''' <TransferGroup UUID="6ee43b88-c248-427d-8107-c4144624bbab" CheckBox="ON">
        <tag Value="-1"/>
        <Method Value="CadID"/>
        <SourceBodies>
        <Entities>
        <Model>'''+ model1 +'''</Model>
        <Body></Body>
        </Entities>
        </SourceBodies>
        <TargetBodies>
        <Entities>
        <Model>'''+ model2 +'''</Model>
        <Body></Body>
        </Entities>
        </TargetBodies>
        <RemoveEntitiesFromGroup Value="1"/>
        <Tolerance Value="0.001"/>
        </TransferGroup>'''
        simlab.execute(TransferGroup)

        # delete empty group after transfering groups to fem
        femGrps = simlab.getGroupsWithSubString("FaceGroup",["*"])
        for thisGrp in femGrps:
            grpEntities = simlab.getEntityFromGroup(thisGrp)
            if not grpEntities:
                self.Logger.info("delete empty group {}".format(thisGrp))
                deleteGrp(thisGrp)
        return 1
    
    def mergeAllBodiesByName(self, bodyNm = None):
        if not bodyNm:
            bodyNames = set(simlab.getBodiesWithSubString(simlab.getModelName("CAD"), ['*']))
            for thisBody in bodyNames:
                thisBodyLst = simlab.getBodiesWithSubString(simlab.getModelName("FEM"),[thisBody+'*'])
                if len(thisBodyLst) > 1 :
                    mergeBodies(thisBodyLst, outputNm=thisBody)
        else:
            bodyNames = simlab.getBodiesWithSubString(simlab.getModelName("FEM"), ['*'])
            if len(bodyNames) > 1:
                mergeBodies(bodyNames, outputNm = bodyNm)

    def meshQualityCleanUp(self):
        self.Logger.info("Mesh quality clean up on aspect ratio")
        modelNm = simlab.getModelName("FEM")
        QualityCheck=''' <QCheck UUID="412da11b-2793-4c07-a058-e49f209f007d">
        <ElementType Value="Tri"/>
        <Option Value="Cleanup"/>
        <Quality LimitValue="$MainAspectRatio" Condition="G Than Or Eq" Name="Aspect Ratio"/>
        <SupportEntities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body></Body>
        </Entities>
        </SupportEntities>
        <CleanupType Value="Local Re-mesh"/>
        <PreserveSurfaceSkew Check="0" Value="55"/>
        </QCheck>'''
        simlab.execute(QualityCheck)
    
    def intersectionCheck(self):
        for this_tol in [1e-06, 1e-03]:
            self.Logger.info("Checking intersections at tolerance, {}".format(this_tol))
            modifyIntersection(this_tol)
            if not simlab.isGroupPresent("INTERSECT_ELEMENT"): 
                self.Logger.info("No intersections found")
                continue
            self.Logger.info("Found intersections!!!")
            elems = simlab.getEntityFromGroup("INTERSECT_ELEMENT")
            if simlab.isGroupPresent(self.INTERSECTION_GROUP):deleteGrp(self.INTERSECTION_GROUP)
            createElementGroup(self.INTERSECTION_GROUP, elems)
            self.exportSlb("Intersections_{}.slb".format(this_tol))
            faceDict = {}
            elems = simlab.getEntityFromGroup(self.INTERSECTION_GROUP)
            for thisElem in elems:
                faceEnt = faceFromElem(thisElem)
                if faceEnt and faceEnt in faceDict:faceDict[faceEnt].append(thisElem)
                else:faceDict[faceEnt] = [thisElem]
            for key in faceDict:
                faceGroups = [aGroup for aGroup in simlab.getGroupsWithSubString("FaceGroup",["*_SM"]) if "Green" in aGroup or "White" in aGroup or "Custom"]
                for thisGrp in faceGroups:
                    faceEnts = list(simlab.getEntityFromGroup(thisGrp))
                    if key in faceEnts:
                        self.Logger.info("The associated Face ID: {} of a group, {}".format(key, thisGrp))
                        deleteElems(faceDict[key])
                        updateModel()
                        grpEnts_before = list(simlab.getEntityFromGroup(thisGrp))
                        if simlab.isGroupPresent("Fill_Hole_Faces"):deleteGrp("Fill_Hole_Faces")
                        meshSize = simlab.getDoubleParameter("$MainMeshSize")
                        fillholesOnBodies(remeshOn=True, remeshSize=meshSize)
                        filledFaceEnts = list(simlab.getEntityFromGroup("Fill_Hole_Faces"))
                        filledFaceEnts.extend(grpEnts_before)
                        mergeFaces(filledFaceEnts)
                        updateModel()
                        faceDict[key]=None
            for key in faceDict:
                if faceDict[key]:
                    self.Logger.info("The associated Face ID: {}".format(key))
                    deleteElems(faceDict[key])
                    updateModel()
                    meshSize = simlab.getDoubleParameter("$MainMeshSize")
                    fillholesOnBodies(remeshOn=True, remeshSize=meshSize)
                    updateModel()
            deleteGrp(self.INTERSECTION_GROUP)

        # if simlab.isGroupPresent(self.INTERSECTION_GROUP):
        #     elemEnts = simlab.getEntityFromGroup(self.INTERSECTION_GROUP)
        #     if not elemEnts: 

    def mergeAllDSFaces(self):
        self.Logger.info("Merge All DS faces, green and white color groups")
        faceGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*_SM"]) if ("White" in thisGrp) or ("Green" in thisGrp)]
        for thisGrp in faceGrps:
            faceEnts = simlab.getEntityFromGroup(thisGrp)
            mergeFaces(faceEnts)
            updateModel()
    
    def createPLDSNodeSets(self):
        # Create DS Node groups
        self.Logger.info("Creating DS Node Groups")
        for thisColor in ["Green","White"]:
            createDSNodeGrp(thisColor, "{}_DSNodes".format(thisColor))
        allDSGrp = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*DSNodes"])]
        faceEnts = []
        for dsGrp in allDSGrp:
            faceEnts.extend(list(simlab.getEntityFromGroup(dsGrp)))
        if faceEnts:createFaceGroup("All_DSNodes", faceEnts)

        # Create PL Node groups
        self.Logger.info("Creating PL node Groups")
        createPLNodeGrp()

        # Create DS and PL node sets
        self.Logger.info("Creating PL and DS Node sets")
        dsNodesGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*DSNodes"]) if not "White" in thisGrp]
        for thisGrp in dsNodesGrps:
            autoSetCreation(thisGrp)
        
        plNodesGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("EdgeGroup",["*PLNodes"]) if not "White" in thisGrp]
        for thisGrp in plNodesGrps:
            autoSetCreation(thisGrp)
        
        # Create Custom color node sets
        customNodeGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*_SM"]) if "Custom" in thisGrp]
        for thisGrp in customNodeGrps:
            autoSetCreation(thisGrp)

    def volumeMesh(self, optionCsv):
        advOption = {}
        with open(optionCsv, "r") as f:
            lines = f.readlines()
            for this_line in lines:
                if not this_line.startswith("#"):
                    spline = this_line.strip().split(",")
                    advOption[spline[0]] = spline[1]

        self.Logger.info("3D Meshing....")
        modelNm = simlab.getModelName("FEM")
        VolumeMesh=''' <VolumeMesher UUID="83822e68-12bb-43b9-b2ac-77e0b9ea5149">
        <tag Value="-1"/>
        <Name Value="VolumeMesher1"/>
        <SupportEntities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body></Body>
        </Entities>
        </SupportEntities>
        <MeshType Value="Tet4"/>
        <AverageElemSize Value="$TetElemSize"/>
        <MaxElemSize Value="Default" Checked="0"/>
        <InternalGrading Value="$TetGradeFactor"/>
        <MinQuality Value="$TetMinSize"/>
        <LinearQuality Value="0"/>
        <MaxQuality Value="1"/>
        <QuadMinQuality Value="0.001"/>
        <QuadQuality Value="0"/>
        <QuadMaxQuality Value="1"/>
        <CadBody Value="0"/>
        <AdvancedOptions>
        <MeshDensity Value="'''+ advOption["MeshDensity"] +'''"/>
        <CreateVol Value="'''+ advOption["CreateVol"] +'''"/>
        <OutputModelName Value="'''+ advOption["OutputModelName"] +'''"/>
        <Assembly Value="'''+ advOption["Assembly"] +'''"/>
        <PreserveFaceMesh Value="'''+ advOption["PreserveFaceMesh"] +'''"/>
        <MeshAsSingleBody Value="'''+ advOption["MeshAsSingleBody"] +'''"/>
        <Retain2DSurfaceBodies Value="'''+ advOption["Retain2DSurfaceBodies"] +'''"/>
        <PreserveSurfaceSkew Value="55" Checked="0"/>
        </AdvancedOptions>
        </VolumeMesher>'''
        simlab.execute(VolumeMesh)
    
    def importSlb(self, fName):
        self.Logger.info("Importing slb model {}".format(fName))
        ImportSlb=''' <ImportSlb CheckBox="ON" UUID="C806F6DF-56FA-4134-9AD1-1010BF292183" gda="">
        <tag Value="1"/>
        <Name Value=""/>
        <FileName Value="'''+ fName +'''"/>
        <ImportOrOpen Value="0"/>
        <Output/>
        </ImportSlb>'''
        simlab.execute(ImportSlb)
    
    def unmergeBody(self):
        self.Logger.info("Unmerge Bodies")
        modelNm = simlab.getModelName("FEM")
        UnmergeBody=''' <UnMerge UUID="B4A72790-34D2-4ac0-9820-84ED4F33E27E" gda="">
        <tag Value="-1"/>
        <Name Value=""/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model> 
        <Body></Body>
        </Entities>
        </SupportEntities>
        <Output/>
        </UnMerge>'''
        simlab.execute(UnmergeBody)
        bodyNames = list(set(simlab.getBodiesWithSubString(simlab.getModelName("CAD"), ['*'])))
        if "Tub" in bodyNames:bodyNames.remove("Tub")
        for thisBody in bodyNames:
            thisBodyLst = simlab.getBodiesWithSubString(simlab.getModelName('FEM'),[thisBody+'*'])
            mergeBodies(thisBodyLst, outputNm=thisBody)
        if "Seal" in bodyNames:
            deleteEntities("Seal")

    def checkAnode(self):
        hozoAnode = False
        backAnode = False

        femFaceGrps = simlab.getGroupsWithSubString("FaceGroup", ["*_SM"])
        for thisGrp in femFaceGrps:
            if "Yellow" in thisGrp:
                backAnode = True
                if backAnode:self.Logger.info("The given cad model has yellow face")
            if "Orange" in thisGrp:
                hozoAnode = True
                if hozoAnode:self.Logger.info("The given cad model has orange face")
        
        return backAnode, hozoAnode
    
    def createCathodeNodeElemSets(self):
        self.Logger.info("Create cathode node sets")
        # Cathode, Seihin, Anode in CAD will be Cathode
        cathodeBodies = []
        for thisBody in ["Cathode","Antena","Seihin"]:
            bodies = simlab.getBodiesWithSubString(simlab.getModelName("FEM"),["{}*".format(thisBody)])
            for aBody in bodies:
                cathodeBodies.append(aBody)
        
        if len(cathodeBodies) > 1:mergeBodies(cathodeBodies, "Cathode")
        else:
            renameBody(cathodeBodies[0], "Cathode")
            updateModel()
        deleteSolidElem("Cathode")
        createNodeSets("Cathode", "CathodeNodes")
        createShellElemSets("Cathode", "CathodeElems")

    def exportFEMNEU(self, anlsType, femNm, neuNm, slbnm = None):
        if anlsType == "Shu":
            self.prepareAnalysis(anlsType, femNm, neuNm)
        elif anlsType == "Back":
            deleteEntities("Anode")
            delProp("Anode")
            deleteSets("ShellElementSet", "AnodeElems")
            self.prepareAnalysis(anlsType, femNm, neuNm)
        elif anlsType == "Hozo":
            cadModelNm = simlab.getModelName("CAD")
            femModelNm = simlab.getModelName("FEM")
            delModel(cadModelNm)
            delModel(femModelNm)
            delMat("Material1")
            delProp()
            deleteSets("NodeSet")
            deleteSets("ShellElementSet")
            self.importSlb(slbnm)
            self.unmergeBody()
            updateModel()
            self.createCathodeNodeElemSets()
            self.prepareAnalysis(anlsType, femNm, neuNm)

    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.info("No such file or directory : {}".format(f_name))
            return False
        return True
    
    def removeFreeEdges(self):
        femBodies = list(simlab.getBodiesWithSubString(simlab.getModelName("FEM"),['*']))
        meshSize = simlab.getDoubleParameter("$MainMeshSize")
        if "Tub" in femBodies:femBodies.remove("Tub")
        if "Seal" in femBodies:femBodies.remove("Seal")
        
        fillholesOnBodies(remeshOn= True, remeshSize=meshSize)

    def prepareAnalysis(self, anlsType, femNm, neuNm):
        self.Logger.info("Create Anode elment sets for {}".format(anlsType))
        createAnodeElemSets(anlsType)
        modelNm = simlab.getModelName("FEM")
        Material=''' <Material UUID="31d13165-03f9-4e35-b548-a88621b8562a">
        <tag Value="-1"/>
        <Name Value="Material1"/>
        <Category Value="Metal"/>
        <Type Value="Isotropic"/>
        <Model Value="Elastic"/>
        <MaterialId Value="2"/>
        <TableData>
        <Youngs_modulus table="" Type="4" Value="208000"/>
        <Shear_modulus table="" Type="4" Value=""/>
        <Poissons_ratio table="" Type="4" Value="0.30"/>
        <Density table="" Type="4" Value="7.8e-9"/>
        <Thermal_Expansion table="" Type="4" Value="0.0"/>
        <Reference_Temperature table="" Type="4" Value="20"/>
        <Damping_coefficient table="" Type="4" Value=".1"/>
        <Stress_Tension table="" Type="4" Value="0.00"/>
        <Stress_Compression table="" Type="4" Value="0.00"/>
        <Stress_Shear table="" Type="4" Value="0.00"/>
        <Mat_Cord_Sys table="" Type="4" Value="0"/>
        <Thermal_conductivity table="" Type="4" Value="4.98100E-02"/>
        <Heat_capacity table="" Type="4" Value="0.5"/>
        <Free_Convection table="" Type="4" Value="0.00"/>
        <Dynamic_Viscosity table="" Type="4" Value="0.00"/>
        <Heat_Generation table="" Type="4" Value="1.00"/>
        <Reference_Enthalpy table="" Type="4" Value="0.00"/>
        <TCH table="" Type="4" Value="0.00"/>
        <TDELTA table="" Type="4" Value="0.00"/>
        <QLAT table="" Type="4" Value="0.00"/>
        </TableData>
        </Material>'''
        simlab.execute(Material)

        # Tub in Solid
        AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
        <tag Value="-1"/>
        <Name Value="$MekkiekiProp"/>
        <Dimension Value="Solid"/>
        <Type Value="Isotropic"/>
        <ID Value="$MekkiekiPID"/>
        <Material Value="Material1"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"Tub",</Body>
        </Entities>
        </SupportEntities>
        <UseExistingPropertyCheck Value="0"/>
        <CoordSystem Value=""/>
        <TableData>
        <WriteMaterial Value="1" Type="2"/>
        <Abaqus_Element_Type Value="0" Type="3"/>
        <OptiStruct_Explicit_Element_Type Value="0" Type="3"/>
        <Ansys_Element_Type Value="0" Type="3"/>
        <Integration_type Value="0" Type="3"/>
        </TableData>
        <Composite/>
        </Property>'''
        simlab.execute(AnalysisProperty)

        # Cathode Shell
        AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
        <tag Value="-1"/>
        <Name Value="$CathodeProp"/>
        <Dimension Value="Shell"/>
        <Type Value="Isotropic"/>
        <ID Value="$CathodePID"/>
        <Material Value="Material1"/>
        <SupportEntities>
        <Entities>
        <Model>'''+modelNm+'''</Model>
        <Body>"Cathode",</Body>
        </Entities>
        </SupportEntities>
        <UseExistingPropertyCheck Value="0"/>
        <TableData>
        <Type Type="3" Value="0"/>
        <Thickness table="" Type="4" Value="1.0"/>
        <SectionIntegration Type="3" Value="0"/>
        <No_of_Integration_Points Type="1" Value="5"/>
        <Remove_locking Type="4" Value="0"/>
        <WriteMaterial Type="2" Value="1"/>
        <Abaqus_Element_Type Type="3" Value="0"/>
        <Nastran_Element_Type Type="3" Value="0"/>
        <Material_Bending Type="3" Value="None"/>
        <Bending_MI_Ratio Type="4" Value="1.0"/>
        <Material_TS Type="3" Value="None"/>
        <TS_Ratio Type="4" Value="0.8333"/>
        <NSM Type="4" Value="0"/>
        <Ansys_Element_Type Type="3" Value="0"/>
        </TableData>
        <Composite/>
        </Property>'''
        simlab.execute(AnalysisProperty)

        # Anode Shell
        APID = simlab.getIntParameter("$AnodePID")
        AnalysisProperty=''' <Property UUID="FAABD80A-7FA2-4d2a-961B-BFA06A361A4C">
        <tag Value="-1"/>
        <Name Value="$AnodeProp"/>
        <Dimension Value="Shell"/>
        <Type Value="Isotropic"/>
        <ID Value="'''+ str(APID) +'''"/>
        <Material Value="Material1"/>
        <SupportEntities>
        <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Body>"Anode",</Body>
        </Entities>
        </SupportEntities>
        <UseExistingPropertyCheck Value="0"/>
        <TableData>
        <Type Type="3" Value="0"/>
        <Thickness table="" Type="4" Value="1.0"/>
        <SectionIntegration Type="3" Value="0"/>
        <No_of_Integration_Points Type="1" Value="5"/>
        <Remove_locking Type="4" Value="0"/>
        <WriteMaterial Type="2" Value="1"/>
        <Abaqus_Element_Type Type="3" Value="0"/>
        <Nastran_Element_Type Type="3" Value="0"/>
        <Material_Bending Type="3" Value="None"/>
        <Bending_MI_Ratio Type="4" Value="1.0"/>
        <Material_TS Type="3" Value="None"/>
        <TS_Ratio Type="4" Value="0.8333"/>
        <NSM Type="4" Value="0"/>
        <Ansys_Element_Type Type="3" Value="0"/>
        </TableData>
        <Composite/>
        </Property>'''
        simlab.execute(AnalysisProperty)

        self.Logger.info("Exporting analysis properties in {} and {}".format(femNm, neuNm))

        # FEM Export
        ExportandSolve=''' <ExportStaticSolverInput UUID="f009bc99-991f-43b7-8c87-cc606ef9c443" pixmap="solution">
        <tag Value="-1"/>
        <Name Value="ExportStaticSolverInput1"/>
        <SolverName Value="OPTISTRUCT" Version="0"/>
        <FileName Value="'''+ femNm +'''"/>
        <WriteMode ValueText="Default" Value="0"/>
        <LoadCase Value="Default"/>
        <Renumber Value="0"/>
        <RunSolver Value="0"/>
        <DataCheck Value="0"/>
        <RemoveOrphanNodes Value="1"/>
        <Version Value="14"/>
        <ExportOptionsVersion Value="1"/>
        <AnalysisType Value="LINEAR" Index="0">
        <CATEGORY_Export_Options key="CATEGORY_Export_Options" ValueText="" decoration="0" name="Export Options"/>
        <Title key="Title" type="string" ValueText="Linear Static Step" decoration="0" name="Title" Value="Linear Static Step"/>
        <Format key="Format" type="int" ValueText="Small Field" decoration="0" name="Format" Value="0"/>
        <Numbering key="Numbering" type="int" ValueText="Ascending Order" decoration="0" name="Numbering" Value="0"/>
        <Write_Linear_Elements key="Write_Linear_Elements" type="check" ValueText="False" decoration="0" name="Write Linear Elements" Value="0"/>
        <Spring_Element_Card_Format key="Spring_Element_Card_Format" type="int" ValueText="CELAS1" decoration="0" name="Spring Element Card Format" Value="0"/>
        <Write_Contact_Slave_Surface_as_SURF key="Write_Contact_Slave_Surface_as_SURF" type="check" ValueText="False" decoration="0" name="Write Contact Slave Surface as SURF" Value="0"/>
        <Write_Enforced_Displacements_as_SPCD key="Write_Enforced_Displacements_as_SPCD" type="check" ValueText="True" decoration="0" name="Write Enforced Displacements as SPCD" Value="1"/>
        <CATEGORY_Material key="CATEGORY_Material" ValueText="" decoration="0" name="Material"/>
        <Write_Material key="Write_Material" type="check" ValueText="True" decoration="0" name="Write Material" Value="1"/>
        <External_File key="External_File" type="string" ValueText="" decoration="32" name="External File" Value=""/>
        <CATEGORY_Spawn_Solver_Options key="CATEGORY_Spawn_Solver_Options" ValueText="" decoration="0" name="Spawn Solver Options"/>
        <Number_of_Processors key="Number_of_Processors" type="int" ValueText="0" decoration="0" name="Number of Processors" Value="0"/>
        <RAM_Allocation key="RAM_Allocation" type="int" ValueText="0" decoration="0" name="RAM Allocation" Value="0"/>
        <Additional_Arguments key="Additional_Arguments" type="string" ValueText="" decoration="0" name="Additional_Arguments" Value=""/>
        </AnalysisType>
        </ExportStaticSolverInput>'''
        simlab.execute(ExportandSolve)

        # NEU Export
        ExportandSolve=''' <ExportStaticSolverInput UUID="f009bc99-991f-43b7-8c87-cc606ef9c443" pixmap="solution">
        <tag Value="-1"/>
        <Name Value="ExportStaticSolverInput1"/>
        <SolverName Value="FEMAP" Version="0"/>
        <FileName Value="'''+ neuNm +'''"/>
        <WriteMode ValueText="Default" Value="0"/>
        <LoadCase Value="Default"/>
        <Renumber Value="0"/>
        <RunSolver Value="0"/>
        <DataCheck Value="0"/>
        <RemoveOrphanNodes Value="1"/>
        <Version Value="14"/>
        <ExportOptionsVersion Value="1"/>
        <AnalysisType Value="LINEAR" Index="0">
        <CATEGORY_Export_Options key="CATEGORY_Export_Options" ValueText="" decoration="0" name="Export Options"/>
        <Description key="Description" type="string" ValueText="Linear Static Analysis" decoration="0" name="Description" Value="Linear Static Analysis"/>
        <CATEGORY_Material key="CATEGORY_Material" ValueText="" decoration="0" name="Material"/>
        <Write_Material key="Write_Material" type="check" ValueText="True" decoration="0" name="Write Material" Value="1"/>
        <External_File key="External_File" type="string" ValueText="" decoration="32" name="External File" Value=""/>
        </AnalysisType>
        </ExportStaticSolverInput>'''
        simlab.execute(ExportandSolve)
    
def quitProgram():
    # self.Logger.info("Quit Simlab application")
    simlab.quitApplication()

def writeToFile(fname, append_write, lineLst):
        with open(fname, append_write) as f:
            f.write('\n'.join(lineLst))

def faceFromElem(elemId):
    modelNm = simlab.getModelName("FEM")
    SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
    <InputElement Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ str(elemId) +''',</Element>
    </Entities>
    </InputElement>
    <Option Value="Faces"/>
    <Groupname Value="SelectFace"/>
    </SelectElementAssociatedEntities>'''
    simlab.execute(SelectElementAssociatedEntities)

    faceEnt = simlab.getEntityFromGroup("SelectFace")
    deleteGrp("SelectFace")
    return faceEnt[0] if faceEnt else None

def deleteElems(elemIds):
    modelNm = simlab.getModelName("FEM")
    DeleteElement=''' <DeleteElement CheckBox="ON" UUID="8d996aff-8ed7-4e5e-9637-b4f75ded7c2c">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ ','.join('{}'.format(v) for v in elemIds) +''',</Element>
    </Entities>
    </SupportEntities>
    <FreeEdgeDisplay Value="0"/>
    <NonManifoldDisplay Value="0"/>
    </DeleteElement>'''
    simlab.execute(DeleteElement)

def createPLNodeGrp():
    faceGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*_DSNodes"])]
    for thisGrp in faceGrps:
        if ("Green" in thisGrp) or ("All" in thisGrp):
            createBodyFromGroup(thisGrp)
            edgeGrpName = '{}_PLNodes'.format(thisGrp.split("_")[0])
            createBodyEdgeGrp(thisGrp, edgeGrpName)
            mergeBodies(['Seihin', thisGrp], outputNm='Seihin')

def createDSNodeGrp(forColor, groupNm):
    faceGrps = [thisGrp for thisGrp in simlab.getGroupsWithSubString("FaceGroup",["*_SM"]) if forColor in thisGrp]
    faceEnts = []
    for thisGrp in faceGrps:
        faceEnts.extend(simlab.getEntityFromGroup(thisGrp))
    if faceEnts:
        createFaceGroup(groupNm, faceEnts)

    if forColor == "Green":
        greenGrps = simlab.createGroupsOfConnectedEntities(groupNm)
        counter = 1
        for thisGreen in greenGrps:
            renameGrp(thisGreen, "Green{}_DSNodes".format(counter))
            counter += 1

def createAnodeElemSets(anlsType):
    if anlsType == "Shu":anodeGrpNm = "Pink_SM"
    elif anlsType == "Back":anodeGrpNm = "Yellow_SM"
    elif anlsType == "Hozo":anodeGrpNm = "Orange_SM"

    deleteEntities("Anode")
    createBodyFromGroup(anodeGrpNm, option = 0)
    renameBody(anodeGrpNm, "Anode")
    createShellElemSets("Anode", "AnodeElems")

def updateModel():
    modelNm = simlab.getModelName("FEM")
    UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
    <tag Value="-1"/>
    <ModelName Value='''+ modelNm +'''/>
    </UpdateMTopology>'''
    simlab.execute(UpdateModel)

def modifyIntersection(tol):
    modelNm = simlab.getModelName("FEM")
    ModifyIntersections=''' <Intersection UUID="9b88366a-d021-40ea-a7a4-2ff23f864a2d">\
    <SupportEntities>
    <Entities>
    <Model>'''+modelNm+'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <IntersectionCheck Value="1"/>
    <Tri_TriOverlapCheck Value="0"/>
    <Edge_TriOverlapCheck Value="0"/>
    <PentrationCheck Value="0"/>
    <Tolerance Value="'''+ str(tol) +'''"/>
    <GrpName Check="0" Name="Element_Group_4"/>
    <Operation Value="Show intersection"/>
    <SkipFaceNormal flag="false"/>
    </Intersection>'''
    simlab.execute(ModifyIntersections)

def fillholesOnBodies(remeshOn = False, remeshSize = 2.0):
    modelNm = simlab.getModelName("FEM")
    localRemesh = str(1) if remeshOn else str(0)
    meshSize = str(remeshSize)

    FillHoles='''<FillHole CheckBox="ON" UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F">
    <tag Value="-1"/>
    <Name Value="FillHole1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+modelNm+'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <Option Value="0"/>
    <Cylindercal_Face Value="0"/>
    <Single_Face Value="0"/>
    <FillPartialLoop Value="0"/>
    <MeshSize LocalReMesh="'''+ localRemesh +'''" Value="'''+ meshSize +'''"/>
    </FillHole>'''
    simlab.execute(FillHoles)

def mergeBodies(bodyNms, outputNm=""):
    modelNm = simlab.getModelName("FEM")
    MergeBodies=''' <BodyMerge UUID="FA9128EE-5E6C-49af-BADF-4016E5622020" gda="">
    <tag Value="-1"/>
    <Name Value="BodyMerge2"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>'''+ ','.join('"{}"'.format(v) for v in bodyNms) +''',</Body>
    </Entities>
    </SupportEntities>
    <Delete_Shared_Faces Value="0"/>
    <Output_Body_Name Value="'''+ outputNm +'''"/>
    <Output/>
    </BodyMerge>'''
    simlab.execute(MergeBodies)
    updateModel()

def mergeFaces(FaceIds):
    modelNm = simlab.getModelName("FEM")
    MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
    <tag Value="-1"/>
    <Name Value="MergeFace1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Face>'''+ ','.join(str(v) for v in FaceIds) +''',</Face>
    </Entities>
    </SupportEntities>
    <MergeBoundaryEdges Value="1"/>
    <SplitBoundaryEdges Value="0"/>
    <SplitEdgesBasedon Value="0"/>
    <FeatureAngle Value="45"/>
    </MergeFace>'''
    simlab.execute(MergeFaces)


def createFaceGroup(grpNm, FaceEntitiesList):
    modelNm = simlab.getModelName("FEM")
    CreateGroup=''' <CreateGroup CheckBox="OFF" isObject="4" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
    <tag Value="-1"/>
    <Name OldValue="" Value="'''+ grpNm +'''"/>
    <SupportEntities>
    <Entities>
        <Model>'''+ modelNm +'''</Model>
        <Face>'''+ ','.join(str(v) for v in FaceEntitiesList)+''',</Face>
    </Entities>
    </SupportEntities>
    <Type Value="Face"/>
    <Color Value="183,168,107,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def createElementGroup(grpNm, elemIds):
    modelNm = simlab.getModelName("FEM")
    CreateGroup=''' <CreateGroup isObject="4" CheckBox="OFF" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''" OldValue=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Element>'''+ ",".join(str(v) for v in elemIds) +''',</Element>
    </Entities>
    </SupportEntities>
    <Type Value="Element"/>
    <Color Value="196,91,7,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)


def createEdgeGroup(grpNm, edgeEntitiesList):
    modelNm = simlab.getModelName("FEM")
    CreateGroup=''' <CreateGroup CheckBox="OFF" UUID="899db3a6-bd69-4a2d-b30f-756c2b2b1954" isObject="4">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''" OldValue=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Edge>'''+ ','.join(str(v) for v in edgeEntitiesList)+''',</Edge>
    </Entities>
    </SupportEntities>
    <Type Value="Edge"/>
    <Color Value="0,30,94,"/>
    <Dup Value="0"/>
    </CreateGroup>'''
    simlab.execute(CreateGroup)

def createBodyFromGroup(grpNm, option = 1):
    # option 1 : Remove the selected face entities from parents body
    # option 0 : Create duplicate body from the selected face entities

    grpEnt = ','.join(str(v) for v in grpNm) if isinstance(grpNm, list) or isinstance(grpNm, tuple) else str(grpNm)

    CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
    <SupportEntities ModelIds="" Value="" EntityTypes=""/>
    <ShareBoundaryEdges Value="1"/>
    <CreateBodyFromFaceOption Value="'''+ str(option) +'''"/>
    <CreateBodyForEachGroup Value="false"/>
    <Group Entity="" Value="'''+ grpEnt +''',"/>
    <UseInputBodyName Value="true"/>
    </BodyFromFaces>'''
    simlab.execute(CreateBodyFromFaces)

def createBodyEdgeGrp(bodyNm, grpNm):
    modelNm = simlab.getModelName("FEM")
    SelectBodyAssociatedEntities=''' <SelectBodyAssociatedEntities UUID="f3c1adc7-fbac-4d30-9b29-9072f36f1ad4">
    <InputBody Values="">
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </InputBody>
    <Option Value="Edges"/>
    <Groupname Value="'''+ grpNm +'''"/>
    </SelectBodyAssociatedEntities>'''
    simlab.execute(SelectBodyAssociatedEntities)

def renameGrp(grpNm, newGrpNm):
    RenameGroupControl=''' <RenameGroupControl CheckBox="ON" UUID="d3addb85-3fd0-4972-80af-e699f96e9045">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +'''"/>
    <NewName Value="'''+ newGrpNm +'''"/>
    <Output/>
    </RenameGroupControl>'''
    simlab.execute(RenameGroupControl)

def autoSetCreation(grpNm):
    AutomaticSetsCreation=''' <AutomaticSetsCreation UUID="be1954dd-1c15-4b38-8a30-c43f8b4c4ff2">
    <tag Value="-1"/>
    <Option Name="Group Name" Value="'''+ grpNm +'''"/>
    <AutoSetEntities>
    <Group>"'''+ grpNm +'''",</Group>
    </AutoSetEntities>
    <ElemType Value="0"/>
    </AutomaticSetsCreation>'''
    simlab.execute(AutomaticSetsCreation)

def fillCracks():
    modelNm = simlab.getModelName("FEM")
    FillCracks=''' <FillCrack CheckBox="ON" UUID="DAE88A9F-E46D-44b7-A534-E94A5D1A716E">
    <tag Value="-1"/>
    <Name Value="FillCrack1"/>
    <SupportEntities>
    <Entities>
    <Model>'''+modelNm+'''</Model>
    <Body></Body>
    </Entities>
    </SupportEntities>
    <RemoveNonManifoldEdges Value="0"/>
    <MaxAngle Value="110"/>
    <MinEdgeLength Value="0.1"/>
    </FillCrack>'''
    simlab.execute(FillCracks)

def createParam(atype, name, value):
    if atype == 'string':
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Type="string" Value="'''+ value +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)
    elif atype == 'real':
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Type="real" Value="'''+ str(value) +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)
    elif atype == 'int':
        SimLabParameters=''' <Parameters UUID="67a54923-dbd3-4d54-931b-2405601ba45f">
        <ParamInfo Type="integer" Value="'''+ str(value) +'''" Name="'''+ name +'''"/>
        </Parameters>'''
        simlab.execute(SimLabParameters)

def deleteSolidElem(bodyNm):
    modelNm = simlab.getModelName('FEM')
    DeleteSolidElements=''' <DeleteSolidElements CheckBox="ON" UUID="c86ce926-2412-4325-a87f-ee6cb66c4de3">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    <Output/>
    </DeleteSolidElements>'''
    simlab.execute(DeleteSolidElements)

def createNodeSets(bodyNm, setName):
    modelNm = simlab.getModelName("FEM")
    Sets=''' <SetsDlg UUID="c54659af-2627-4c1a-b516-f5312356c88d" isObject="2" customselection="1" BCType="Sets" CheckBox="ON" pixmap="sets">
    <tag Value="-1"/>
    <Name Value="SetsDlg4"/>
    <SetstEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SetstEntities>
    <masterSupportEntities ModelIds="" Value="" EntityTypes=""/>
    <slaveSupportEntities ModelIds="" Value="" EntityTypes=""/>
    <SetName Value="'''+ setName +'''"/>
    <SetType Value="Node"/>
    <EntityType Value="Body"/>
    <EntityID Value=""/>
    <nodeaset Value=""/>
    <nodeaset1 Value=""/>
    <one Value=""/>
    <two Value=""/>
    <three Value=""/>
    <four Value=""/>
    <five Value=""/>
    <six Value=""/>
    <LinearCheck Value=""/>
    <TabIndex Value=""/>
    <Tolerance Value=""/>
    <ContactFaceIndex Value=""/>
    <TrimOption Value="-1"/>
    <MasterSetName Value=""/>
    <SlaveSetName Value=""/>
    <SetTypeIndex Value=""/>
    <MapEntities Value=""/>
    <MeshCtrlCheck Value=""/>
    <SetCtrlCheck Value=""/>
    <GrpCtrlCheck Value=""/>
    <Options Value=""/>
    <CadModelCheck Value=""/>
    <MaxId Value=""/>
    <MinId Value=""/>
    <AxisID Value=""/>
    <RegionType Value="0"/>
    <RegionX Value="0.0"/>
    <RegionY Value="0.0"/>
    <RegionZ Value="0.0"/>
    <Node_IncMidNodes Value="1"/>
    <SurfNodes Value="0"/>
    <IncSolidElemIsAttachFaceNodes Value=""/>
    <NumSolidElemLayers Value=""/>
    <IsRegionType Value="-1"/>
    <IsRegionDefined Value="-1"/>
    <RegnOption Value="-1"/>
    <Cube_PT1 X="" Y="" Z=""/>
    <Cube_PT2 X="" Y="" Z=""/>
    <Cube_PT3 X="" Y="" Z=""/>
    <Cube_PT4 X="" Y="" Z=""/>
    <Cube_PT5 X="" Y="" Z=""/>
    <Cube_PT6 X="" Y="" Z=""/>
    <Cube_PT7 X="" Y="" Z=""/>
    <Cube_PT8 X="" Y="" Z=""/>
    <Cyl_PT1 X="" Y="" Z=""/>
    <Cyl_PT2 X="" Y="" Z=""/>
    <CylRadius Value=""/>
    <CylHeight Value=""/>
    <SphPT1 X="" Y="" Z=""/>
    <SphRadius Value=""/>
    <Output/>
    </SetsDlg>'''
    simlab.execute(Sets)

def createShellElemSets(bodyNm, setName):
    modelNm = simlab.getModelName("FEM")
    Sets=''' <SetsDlg UUID="c54659af-2627-4c1a-b516-f5312356c88d" isObject="2" customselection="1" BCType="Sets" CheckBox="ON" pixmap="sets">
    <tag Value="-1"/>
    <Name Value="SetsDlg5"/>
    <SetstEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SetstEntities>
    <masterSupportEntities ModelIds="" Value="" EntityTypes=""/>
    <slaveSupportEntities ModelIds="" Value="" EntityTypes=""/>
    <SetName Value="'''+ setName +'''"/>
    <SetType Value="Shell Elem"/>
    <EntityType Value="Body"/>
    <EntityID Value=""/>
    <nodeaset Value=""/>
    <nodeaset1 Value=""/>
    <one Value=""/>
    <two Value=""/>
    <three Value=""/>
    <four Value=""/>
    <five Value=""/>
    <six Value=""/>
    <LinearCheck Value="0"/>
    <TabIndex Value=""/>
    <Tolerance Value=""/>
    <ContactFaceIndex Value=""/>
    <TrimOption Value="-1"/>
    <MasterSetName Value=""/>
    <SlaveSetName Value=""/>
    <SetTypeIndex Value=""/>
    <MapEntities Value=""/>
    <MeshCtrlCheck Value=""/>
    <SetCtrlCheck Value=""/>
    <GrpCtrlCheck Value=""/>
    <Options Value=""/>
    <CadModelCheck Value=""/>
    <MaxId Value=""/>
    <MinId Value=""/>
    <AxisID Value=""/>
    <RegionType Value=""/>
    <RegionX Value=""/>
    <RegionY Value=""/>
    <RegionZ Value=""/>
    <Node_IncMidNodes Value=""/>
    <SurfNodes Value=""/>
    <IncSolidElemIsAttachFaceNodes Value=""/>
    <NumSolidElemLayers Value=""/>
    <IsRegionType Value="-1"/>
    <IsRegionDefined Value="-1"/>
    <RegnOption Value="-1"/>
    <Cube_PT1 X="" Y="" Z=""/>
    <Cube_PT2 X="" Y="" Z=""/>
    <Cube_PT3 X="" Y="" Z=""/>
    <Cube_PT4 X="" Y="" Z=""/>
    <Cube_PT5 X="" Y="" Z=""/>
    <Cube_PT6 X="" Y="" Z=""/>
    <Cube_PT7 X="" Y="" Z=""/>
    <Cube_PT8 X="" Y="" Z=""/>
    <Cyl_PT1 X="" Y="" Z=""/>
    <Cyl_PT2 X="" Y="" Z=""/>
    <CylRadius Value=""/>
    <CylHeight Value=""/>
    <SphPT1 X="" Y="" Z=""/>
    <SphRadius Value=""/>
    <Output/>
    </SetsDlg>'''
    simlab.execute(Sets)

def renameBody(oldBdyNm, newBdyNm):
    modelNm = simlab.getModelName("FEM")
    RenameBody=''' <RenameBody UUID="78633e0d-3d2f-4e9a-b075-7bff122772d8" CheckBox="ON">
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ oldBdyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    <NewName Value="'''+ newBdyNm +'''"/>
    <Output/>
    </RenameBody>'''
    simlab.execute(RenameBody)

def deleteEntities(bodyNm):
    modelNm = simlab.getModelName("FEM")
    DeleteEntity=''' <DeleteEntity CheckBox="ON" UUID="BF2C866D-8983-4477-A3E9-2BBBC0BC6C2E">
    <tag Value="-1"/>
    <Name Value=""/>
    <SupportEntities>
    <Entities>
    <Model>'''+ modelNm +'''</Model>
    <Body>"'''+ bodyNm +'''",</Body>
    </Entities>
    </SupportEntities>
    </DeleteEntity>'''
    simlab.execute(DeleteEntity)
    updateModel()

def delMat(name):
    # Delete Material
    DeleteMaterial=''' <DeleteMaterial CheckBox="ON" UUID="0a0b8b68-e63e-40b3-82c6-4e7a5b01936b">
    <Name Value="'''+ name +'''"/>
    </DeleteMaterial>'''
    simlab.execute(DeleteMaterial)

def deleteSets(setType, name = ''):
    # setType
    # 1. NodeSet
    # 2. ShellElementSet

    DeleteLBCControl=''' <DeleteLBCControl UUID="b37a621e-e984-4cee-a307-3a80317852ae" CheckBox="ON">
    <Output/>
    <Name Type="'''+ setType +'''" Value="'''+ name +'''"/>
    </DeleteLBCControl>'''
    simlab.execute(DeleteLBCControl)

def delProp(propNm = 'All'):
    if propNm == 'All':
        # Delete Properties
        DeleteProperty=''' <DeleteProperty UUID="5e9033a8-599c-4f42-a9d2-b3fd54c71136" CheckBox="ON">
        <Name Value=""/>
        </DeleteProperty>'''
        simlab.execute(DeleteProperty)

    else:
        DeleteProperty=''' <DeleteProperty CheckBox="ON" UUID="5e9033a8-599c-4f42-a9d2-b3fd54c71136">
        <Name Value="'''+ propNm +'''"/>
        </DeleteProperty>'''
        simlab.execute(DeleteProperty)

def delModel(modelNm):
    DeleteModel=''' <DeleteModel CheckBox="ON" updategraphics="0" UUID="AE031126-6421-4633-8FAE-77C8DE10C18F">
    <ModelName Value="'''+ modelNm +'''"/>
    </DeleteModel>'''
    simlab.execute(DeleteModel)
    updateModel()

def deleteGrp(grpNm):
    DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
    <tag Value="-1"/>
    <Name Value="'''+ grpNm +''',"/>
    <Output/>
    </DeleteGroupControl>'''
    simlab.execute(DeleteGroupControl)


