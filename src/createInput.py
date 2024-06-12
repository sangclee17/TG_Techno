import os
from Logger import Logger
import shutil

class EPPS_Input():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
        self.NEUSHU1="neu_shu1.txt"
        self.FMOSHU1="fmo_shu1.txt"
        self.NEUHOZO1="neu_hozo1.txt"
        self.FMOHOZO1="fmo_hozo1.txt"
        self.NEUBACK1="neu_back1.txt"
        self.FMOBACK1="fmo_back1.txt"

        self.FEMMAIN = "PreModel.fem"
            
    def create(self, condDict):        
        neuFiles = [f for f in os.listdir() if f.endswith(".neu")]
        if not neuFiles:
            self.Logger.error("Can't find any neu files to process")
            return 0
        
        for neuFile in neuFiles:
            self.Logger.info("Working on {}1.neu ...".format(neuFile.split(".")[0]))
            if "Shu" in neuFile:headerType = "Main"
            elif "Hozo" in neuFile:headerType = "Hozo"
            elif "Back" in neuFile:headerType = "Back"

            # Checking corresponding FEM
            femFile = "{}.fem".format(neuFile.split(".")[0])
            if not self.fileExists(femFile): return 0
            
            writeTo = "{}1.neu".format(neuFile.split(".")[0])

            with open(writeTo, "w") as f_write:
                # NEU1 header
                self.Logger.info("Writing header for the type {}".format(headerType))
                neu1Header = createNEUHeader(headerType, condDict)
                if not neu1Header:return 0
                f_write.write("\n".join(neu1Header))
                
                # Read from NEU
                self.Logger.info("Re-writing from the original neu file {}".format(neuFile))
                with open(neuFile, "r") as f_read:
                    counter = 0
                    for line in f_read:
                        line = line.rstrip()
                        if counter >= 10 :
                            if line == "   601": break 
                            f_write.write("{}\n".format(line))
                        counter += 1

                # Read from FEM
                self.Logger.info("Writing node and elem sets from {}".format(femFile))
                with open(femFile, "r") as f:
                    SKIPLINE, CATHODE_NODE, CATHODE_ELEMS, ANODE_ELEMS = True, False, False, False
                    for line in f:
                        line = line.lower()
                        if line.startswith('$hmset'):
                            SKIPLINE = False
                            if "cathode" in line and "node" in line:
                                lineLst = getLineLst(1)
                                f_write.write("\n".join(lineLst))
                                CATHODE_NODE, CATHODE_ELEMS, ANODE_ELEMS = True, False, False
                            elif "cathode" in line and "elem" in line:
                                lineLst = getLineLst(3)
                                f_write.write("\n".join(lineLst))
                                CATHODE_NODE, CATHODE_ELEMS, ANODE_ELEMS = False, True, False
                            elif "anode" in line and "elem" in line:
                                CATHODE_NODE, CATHODE_ELEMS, ANODE_ELEMS = False, False, True
                            
                        if not SKIPLINE and line.startswith("+"):
                            if CATHODE_NODE:
                                cutp = line.split()
                                for ind, aval in enumerate(cutp):
                                    if ind != 0 and float(aval) > 0:
                                        lineLst = getLineLst(2, aval)
                                        f_write.write("\n".join(lineLst))                            
                            elif CATHODE_ELEMS:               
                                cutp = line.split()
                                for ind, aval in enumerate(cutp):
                                    if ind != 0 and float(aval) > 0:
                                        lineLst = getLineLst(4, aval)
                                        f_write.write("\n".join(lineLst))
                            elif ANODE_ELEMS:
                                cutp = line.split()
                                for ind, aval in enumerate(cutp):
                                    if ind != 0 and float(aval) > 0:
                                        lineLst = getLineLst(5, aval)
                                        f_write.write("\n".join(lineLst))
                    lineLst = getLineLst(6)
                    f_write.write("\n".join(lineLst))

                # Add Comp func
                self.Logger.info("Writing componenet function")
                compLines = createCompfunc(condDict)
                if not compLines:return 0
                f_write.write("\n".join(compLines))

            #Change Fem file name for post
            if headerType == "Main":
                os.rename(femFile, self.FEMMAIN)

            # shutil.copyfile(writeTo, "{}_copy.neu".format(writeTo.split(".")[0]))
            self.createinputFileText(writeTo)
            os.remove(neuFile)

        return 1

    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.error("No such file or directory : {}".format(f_name))
            return False
        return True
    
    def createinputFileText(self, neuName):
        if "Shu" in neuName:
            neufileTXT = self.NEUSHU1
            fmofileTXT = self.FMOSHU1
        elif "Hozo" in neuName:
            neufileTXT = self.NEUHOZO1
            fmofileTXT = self.FMOHOZO1

        elif "Back" in neuName:
            neufileTXT = self.NEUBACK1
            fmofileTXT = self.FMOBACK1

        with open(neufileTXT, "w") as f:
            self.Logger.info("exporting {}".format(neufileTXT))
            f.write(neuName)
            
        with open(fmofileTXT, "w") as f:
            self.Logger.info("exporting {}".format(fmofileTXT))
            fmo = "{}.fmo".format(neuName.split(".")[0])
            lineLst = ["6400000","0", fmo, "1", "0", "0.001", "1"]
            f.write('\n'.join(lineLst))

def writeToFile(fname, append_write, lineLst):
    with open(fname, append_write) as f:
        f.write('\n'.join(lineLst))

def createNEUHeader(headerType, md):
    lineLst = []
    try:
        if headerType == "Main":
            anodeCurrent = md["A019"]
            anodeTime = md["A014"]
        elif headerType == "Hozo":
            anodeCurrent = md["A021"]
            anodeTime = md["A015"]
        elif headerType == "Back":
            anodeCurrent = md["A023"]
            anodeTime = md["A016"]

        lineLst.append("   -1")
        lineLst.append("   100")
        lineLst.append("<NULL>")
        lineLst.append("10., ")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   405")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   475")
        lineLst.append("1,124,0,124,1,1,")
        lineLst.append("0,1,1,0,1,0,0,")
        lineLst.append("3.,0.,0.,")
        lineLst.append("0.,0.,0.,")
        lineLst.append("1,")
        lineLst.append("TG_Ni {} A {} sec".format(anodeCurrent,anodeTime))
        lineLst.append("2,124,0,124,1,1,")
        lineLst.append("0,1,1,0,1,0,0,")
        lineLst.append("3.,3.,0.,")
        lineLst.append("0.,0.,0.,")
        lineLst.append("1,")
        lineLst.append("{},{},{},{},{},{},{},{},{},{},{}".format(md["E001"],md["E002"],md["E003"],md["E004"],md["E005"],md["E006"],md["E007"],md["E008"],md["E009"],md["E010"],md["E011"]))
        lineLst.append("3,124,0,124,1,1,")
        lineLst.append("0,1,1,0,1,0,0,")
        lineLst.append("3.,6.,0.,")
        lineLst.append("0.,0.,0.,")
        lineLst.append("1,")
        lineLst.append("{},{},{},{},{}".format(md["E012"],md["E013"],anodeCurrent,md["E015"],md["E016"]))
        lineLst.append("4,124,0,124,1,1,")
        lineLst.append("0,1,1,0,1,0,0,")
        lineLst.append("3.,9.,0.,")
        lineLst.append("0.,0.,0.,")
        lineLst.append("1,")
        lineLst.append("{},{},{},{},{},{},{},{},{},{}".format(md["E017"],md["E018"],anodeTime,md["E020"],md["E021"],md["E022"],md["E023"],md["E024"],md["E025"],md["E026"]))
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   410")
        lineLst.append("1,")
        lineLst.append("fast")
        lineLst.append("10")
        lineLst.append("10.,")
        lineLst.append("1,")
        lineLst.append("slow")
        lineLst.append("400")
        lineLst.append("400.,")
        lineLst.append("1,")
        lineLst.append("paused")
        lineLst.append("5000")
        lineLst.append("5000.,")
        lineLst.append("1,")
        lineLst.append("realslow")
        lineLst.append("1000")
        lineLst.append("1000.,")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   413")
        lineLst.append("1,124,")
        lineLst.append("Default Layer")
        lineLst.append("9999,124,")
        lineLst.append("Construction Layer")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   570")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   571")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   572")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   573")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   601")
        lineLst.append("{},-601,55,0,0,1,0,".format(md["E049"]))
        lineLst.append("{}".format(md["E050"])) 
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("25,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,")
        lineLst.append("200,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,{},0.,0.,{},0.,{},0.,0.,".format(md["E051"],md["E051"], md["E051"]))
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("50,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("70,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("{},-601,55,0,0,1,0,".format(md["E052"]))
        lineLst.append("Ni")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("25,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,")
        lineLst.append("200,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,{},0.,0.,{},0.,{},{},{},".format(md["E053"],md["E053"],md["E053"],md["E054"],md["E055"]))
        lineLst.append("{},0.,0.,0.,0.,0.,0.,0.,0.,0.,".format(md["E056"]))
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("50,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("70,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("{},-601,55,0,0,1,0,".format(md["E063"]))
        lineLst.append("Ni Anode")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("25,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,")
        lineLst.append("200,")
        lineLst.append("0.,0.,0.,{},{},{},0.,0.,0.,0.0001,".format(md["E064"], md["E064"], md["E064"]))
        lineLst.append("0.,0.,0.,0.,0.,0.0001,0.,0.,0.,0.,")
        lineLst.append("0.0001,0.,0.,0.,{},0.,0.,{},0.,{},".format(md["E064"], md["E064"], md["E064"]))
        lineLst.append("0.0001,0.,0.,0.0001,0.,{},0.,0.,0.,0.,".format(md["E064"]))
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("50,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("70,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("{},-601,55,0,0,1,0,".format(md["E059"]))
        lineLst.append("Ni Cathode")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("25,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,")
        lineLst.append("200,")
        lineLst.append("0.,0.,0.,{},{},{},0.,0.,0.,0.00028,".format(md["E061"],md["E061"],md["E061"]))
        lineLst.append("0.,0.,0.,0.,0.,0.00028,0.,0.,0.,0.,")
        lineLst.append("0.00028,0.,0.,0.,{},0.,0.,{},0.,{},".format(md["E061"],md["E061"],md["E061"]))
        lineLst.append("0.00028,0.,0.,0.00028,0.,{},0.,0.,0.,0.,".format(md["E061"]))
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        lineLst.append("50,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("70,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,0,0,0,0,0,0,0,0,")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   402")
        lineLst.append("{},110,121,25,1,0,0,".format(md["D006"]))
        lineLst.append("{}".format(md["D005"]))
        lineLst.append("0,0,0,0,")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,")
        lineLst.append("75,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0,")
        lineLst.append("0,")
        lineLst.append("{},110,222,17,1,0,0,".format(md["D002"]))
        lineLst.append("{}".format(md["D001"]))
        lineLst.append("0,0,0,0,")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,")
        lineLst.append("75,")
        lineLst.append("1.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("1.,0.8333,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0,")
        lineLst.append("0,")
        lineLst.append("{},110,224,17,1,0,0,".format(md["D004"]))
        lineLst.append("{}".format(md["D003"]))
        lineLst.append("0,0,0,0,")
        lineLst.append("10,")
        lineLst.append("0,0,0,0,0,0,0,0,")
        lineLst.append("0,0,")
        lineLst.append("75,")
        lineLst.append("1.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("1.,0.8333,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0.,0.,0.,0.,0.,")
        lineLst.append("0,")
        lineLst.append("0,")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   926")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   927")
        lineLst.append("   -1")
        lineLst.append("   -1\n")
    except KeyError as e:
        lineLst = []
        self.Logger.error("Check Analysis condition parameter {} ".format(e))

    return lineLst

def createCompfunc(md):
    lineLst = []
    try:
        lineLst.append("   -1")
        lineLst.append("   420")
        lineLst.append("1,0,")
        lineLst.append("Component1")
        lineLst.append("1,{}".format(md["E027"]))
        lineLst.append("2,{}".format(md["E028"]))
        lineLst.append("3,{}".format(md["E029"]))
        lineLst.append("4,{}".format(md["E030"]))
        lineLst.append("5,{}".format(md["E031"]))
        lineLst.append("6,{}".format(md["E032"]))
        lineLst.append("7,{}".format(md["E033"]))
        lineLst.append("8,{}".format(md["E034"]))
        lineLst.append("9,{}".format(md["E035"]))
        lineLst.append("10,{}".format(md["E036"]))
        lineLst.append("11,{}".format(md["E037"]))
        lineLst.append("-1,0.,0.,")
        lineLst.append("2,0,")
        lineLst.append("Component2")
        lineLst.append("1,{}".format(md["E038"]))
        lineLst.append("2,{}".format(md["E039"]))
        lineLst.append("3,{}".format(md["E040"]))
        lineLst.append("4,{}".format(md["E041"]))
        lineLst.append("5,{}".format(md["E042"]))
        lineLst.append("6,{}".format(md["E043"]))
        lineLst.append("7,{}".format(md["E044"]))
        lineLst.append("8,{}".format(md["E045"]))
        lineLst.append("9,{}".format(md["E046"]))
        lineLst.append("10,{}".format(md["E047"]))
        lineLst.append("11,{}".format(md["E048"]))
        lineLst.append("-1,0.,0.,")
        lineLst.append("   -1")
        lineLst.append("   -1")
        lineLst.append("   412")
        lineLst.append("0,1,3,0,0,1,0.,")
        lineLst.append("   -1\n")
    except KeyError as e:
        self.Logger.error("Check Analysis condition parameter {} ".format(e))
        lineLst = []
    return lineLst

def getLineLst(blockNum, value = 0):
    thisLst = []
    # CathodeNodes
    if blockNum == 1:
        thisLst.append("   507")
        thisLst.append("1,")
        thisLst.append("voltage")
        thisLst.append("0,0.,0,0,0,0,0.,")
        thisLst.append("0.,0.,0.,0,0,0,")
        thisLst.append("0.,0.,0.,0,0,0,")
        thisLst.append("0.,0.,0.,")
        thisLst.append("0.,0.,0.,0,0,0,")
        thisLst.append("0.,0.,0.,0,")
        thisLst.append("0.,0.,0.,0.,")
        thisLst.append("0.,0.,0.,0.,")
        thisLst.append("0,0,0,")
        thisLst.append("0,0,0,")
        thisLst.append("0.,0.,0.,0.,")
        thisLst.append("0.,0.,0.,")
        thisLst.append("0.,0.,0.,0.,0.,0.,")
        thisLst.append("0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,")
        thisLst.append("0,0,0,0,0,0,0,0,0,")
        thisLst.append("0,0,0,0,0,0,0,0,")
        thisLst.append("0,0,0,0,0,0,0,0,")
        thisLst.append("0,0,0,0,0,0,0,")
        thisLst.append("0,0,0,0,0,0,0,0,0,0,0,\n")
    elif blockNum == 2:
        thisLst.append("{},3,10,1,0,0,0,3,".format(value))
        thisLst.append("1,1,1,")
        thisLst.append("1.,0.,0.,0.,141.,")
        thisLst.append("0,0,0,0,0,")
        thisLst.append("0,0,0,0,0,")
        thisLst.append("0,0,0,")
        thisLst.append("0.,0.,0.,\n")
    # CathodeElems
    elif blockNum == 3:
        thisLst.append("-1,-1,-1,-1,-1,-1,0,0,")
        thisLst.append("-1,-1,-1,-1,-1,-1,0,0,")
        thisLst.append("-1,-1,-1,0.,0.,-1,1,0,\n")
    elif blockNum == 4:
        thisLst.append("{},10,1,0.,-1.,0,0,1,\n".format(value))
    # AnodeElems
    elif blockNum == 5:
        thisLst.append("{},10,1,1.,-1.,0,0,2,\n".format(value))
    elif blockNum == 6:
        thisLst.append("-1,-1,-1,0.,0.,-1,1,0,")
        thisLst.append("-1,0,-1,0.,-1,")
        thisLst.append("1,16,43,")
        thisLst.append("温度 on ｴﾚﾒﾝﾄ")
        thisLst.append("2,16,43,")
        thisLst.append("温度 on ｴﾚﾒﾝﾄ")
        thisLst.append("3,13,3,")
        thisLst.append("変位 - 並進 on ﾉｰﾄﾞ")
        thisLst.append("-1,0,0,")
        thisLst.append("   -1\n")
    return thisLst

