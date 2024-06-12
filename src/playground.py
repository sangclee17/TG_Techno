# from hwx import simlab

# def faceFromElem(elemId):
#     modelNm = simlab.getModelName("FEM")
#     SelectElementAssociatedEntities=''' <SelectElementAssociatedEntities UUID="7062f057-0e48-4ccc-ad73-e60584e8ff26">
#     <InputElement Values="">
#     <Entities>
#     <Model>'''+ modelNm +'''</Model>
#     <Element>'''+ str(elemId) +''',</Element>
#     </Entities>
#     </InputElement>
#     <Option Value="Faces"/>
#     <Groupname Value="SelectFace"/>
#     </SelectElementAssociatedEntities>'''
#     simlab.execute(SelectElementAssociatedEntities)

#     faceEnt = simlab.getEntityFromGroup("SelectFace")
#     deleteGrp("SelectFace")
#     return faceEnt[0] if faceEnt else None

# def deleteGrp(grpNm):
#     DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
#     <tag Value="-1"/>
#     <Name Value="'''+ grpNm +''',"/>
#     <Output/>
#     </DeleteGroupControl>'''
#     simlab.execute(DeleteGroupControl)

# def updateModel():
#     modelNm = simlab.getModelName("FEM")
#     UpdateModel=''' <UpdateMTopology UUID="D1F56859-D6DB-4431-8699-7E3BE98DA530">
#     <tag Value="-1"/>
#     <ModelName Value='''+ modelNm +'''/>
#     </UpdateMTopology>'''
#     simlab.execute(UpdateModel)

# def deleteElems(elemIds):
#     modelNm = simlab.getModelName("FEM")
#     DeleteElement=''' <DeleteElement CheckBox="ON" UUID="8d996aff-8ed7-4e5e-9637-b4f75ded7c2c">
#     <tag Value="-1"/>
#     <Name Value=""/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+ modelNm +'''</Model>
#     <Element>'''+ ','.join('{}'.format(v) for v in elemIds) +''',</Element>
#     </Entities>
#     </SupportEntities>
#     <FreeEdgeDisplay Value="0"/>
#     <NonManifoldDisplay Value="0"/>
#     </DeleteElement>'''
#     simlab.execute(DeleteElement)

# def createBodyFromGroup(grpNm, option = 1):
#     # option 1 : Remove the selected face entities from parents body
#     # option 0 : Create duplicate body from the selected face entities

#     grpEnt = ','.join(str(v) for v in grpNm) if isinstance(grpNm, list) or isinstance(grpNm, tuple) else str(grpNm)

#     CreateBodyFromFaces=''' <BodyFromFaces UUID="24F7C671-DC40-44e0-9B32-8A22A67F58FA" gda="">
#     <SupportEntities ModelIds="" Value="" EntityTypes=""/>
#     <ShareBoundaryEdges Value="1"/>
#     <CreateBodyFromFaceOption Value="'''+ str(option) +'''"/>
#     <CreateBodyForEachGroup Value="false"/>
#     <Group Entity="" Value="'''+ grpEnt +''',"/>
#     <UseInputBodyName Value="true"/>
#     </BodyFromFaces>'''
#     simlab.execute(CreateBodyFromFaces)

# # def mergeBodies(*args, outputNm=""):
# #     modelNm = simlab.getModelName("FEM")
# #     MergeBodies=''' <BodyMerge UUID="FA9128EE-5E6C-49af-BADF-4016E5622020" gda="">
# #     <tag Value="-1"/>
# #     <Name Value="BodyMerge2"/>
# #     <SupportEntities>
# #     <Entities>
# #     <Model>'''+ modelNm +'''</Model>
# #     <Body>'''+ ','.join('"{}"'.format(v) for v in args) +''',</Body>
# #     </Entities>
# #     </SupportEntities>
# #     <Delete_Shared_Faces Value="0"/>
# #     <Output_Body_Name Value="'''+ outputNm +'''"/>
# #     <Output/>
# #     </BodyMerge>'''
# #     simlab.execute(MergeBodies)
# def fillholesOnBodies(remeshOn = False, remeshSize = 2.0):
#     modelNm = simlab.getModelName("FEM")
#     localRemesh = str(1) if remeshOn else str(0)
#     meshSize = str(remeshSize)

#     FillHoles='''<FillHole CheckBox="ON" UUID="E9B9EC99-A6C1-4626-99FF-626F38A8CE4F">
#     <tag Value="-1"/>
#     <Name Value="FillHole1"/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+modelNm+'''</Model>
#     <Body></Body>
#     </Entities>
#     </SupportEntities>
#     <Option Value="0"/>
#     <Cylindercal_Face Value="0"/>
#     <Single_Face Value="0"/>
#     <FillPartialLoop Value="0"/>
#     <MeshSize LocalReMesh="'''+ localRemesh +'''" Value="'''+ meshSize +'''"/>
#     </FillHole>'''
#     simlab.execute(FillHoles)

# def deleteGrp(grpNm):
#     DeleteGroupControl=''' <DeleteGroupControl CheckBox="ON" UUID="2a3b5834-9708-4b03-871c-6d05623667bd">
#     <tag Value="-1"/>
#     <Name Value="'''+ grpNm +''',"/>
#     <Output/>
#     </DeleteGroupControl>'''
#     simlab.execute(DeleteGroupControl)

# def mergeFaces(FaceIds):
#     modelNm = simlab.getModelName("FEM")
#     MergeFaces=''' <MergeFace UUID="D9D604CE-B512-44e3-984D-DF3E64141F8D">
#     <tag Value="-1"/>
#     <Name Value="MergeFace1"/>
#     <SupportEntities>
#     <Entities>
#     <Model>'''+ modelNm +'''</Model>
#     <Face>'''+ ','.join(str(v) for v in FaceIds) +''',</Face>
#     </Entities>
#     </SupportEntities>
#     <MergeBoundaryEdges Value="1"/>
#     <SplitBoundaryEdges Value="0"/>
#     <SplitEdgesBasedon Value="0"/>
#     <FeatureAngle Value="45"/>
#     </MergeFace>'''
#     simlab.execute(MergeFaces)

# faceDict = {}
# elems = simlab.getEntityFromGroup("INTERSECT_ELEMENT")
# for thisElem in elems:
#     faceEnt = faceFromElem(thisElem)
#     # print("Associated Face to element Id {}:{}".format(thisElem,faceEnt))
#     if faceEnt and faceEnt in faceDict: faceDict[faceEnt].append(thisElem)
#     else:
#         faceDict[faceEnt] = [thisElem]
# print(faceDict)

# for key in faceDict:
#     faceGroups = [aGroup for aGroup in simlab.getGroupsWithSubString("FaceGroup",["*_SM"]) if "Green" in aGroup or "White" in aGroup or "Custom"]
#     for thisGrp in faceGroups:
#         faceEnts = list(simlab.getEntityFromGroup(thisGrp))
#         if key in faceEnts:
#             print("Found group {} that has face id {}".format(thisGrp, key))
#             print("deleted elem ids {}".format(faceDict[key]))
#             deleteElems(faceDict[key])
#             updateModel()
#             grpEnts_before = list(simlab.getEntityFromGroup(thisGrp))
#             print("{} entities before merge:{}".format(thisGrp, grpEnts_before))
#             meshSize = simlab.getDoubleParameter("$MainMeshSize")
#             print(simlab.getBodiesWithSubString(simlab.getModelName("FEM"),["*"]))
#             print("fill holes on body {} and remesh".format(thisGrp))
#             fillholesOnBodies(remeshOn=True, remeshSize=meshSize)

#             filledFaceEnts = list(simlab.getEntityFromGroup("Fill_Hole_Faces"))
#             print("The face filled id is {}".format(filledFaceEnts))
#             filledFaceEnts.extend(grpEnts_before)
#             print("MergeFaces:{}".format(filledFaceEnts))
#             mergeFaces(filledFaceEnts)
#             updateModel()
#             print("update face dict")
#             faceDict[key]=None

# print("fill holes for the rest elements")
# for key in faceDict:
#     if faceDict[key]:
#         print("Associated face:{}\nElements:{}".format(key, faceDict[key]))
#         deleteElems(faceDict[key])
#         updateModel()
#         meshSize = simlab.getDoubleParameter("$MainMeshSize")
#         fillholesOnBodies(remeshOn=True, remeshSize=meshSize)
#         updateModel()
