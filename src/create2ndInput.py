
import os
import sys
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

REN = "RENAME"

class NEU2Writer():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)

        self.NEU2_MAIN_INPUT = "PreModel2.neu"
        self.NEU2_HOZO_INPUT = "PreModel2_hojyo.neu"
        self.NEU3_HOZO_INPUT = "PreModel3_hojyo.neu"

        self.NEUSHU2="neu_shu2.txt"
        self.FMOSHU2="fmo_shu2.txt"
        self.NEUHOZO2="neu_hozo2.txt"
        self.FMOHOZO2="fmo_hozo2.txt"
        self.NEUBACK2="neu_back2.txt"
        self.FMOBACK2="fmo_back2.txt"

        self.NEUHOZO3="neu_hozo3.txt"
        self.FMOHOZO3="fmo_hozo3.txt"

    def getNewCurrentValForShu(self, no, md, ned):
        self.Logger.info("Calculating new current value for the Shu type {}".format(no))
        coeff = 1e-6
        result = None
        currentValueShu = float(md["A019"])
        thickness_Specified = float(md["A017"])
        thickness_Upper_Threshold_DS = float(md["A027"])
        thickness_Upper_Threshold_PL = float(md["A028"])
        thickness_Lower_Threshold = float(md["A026"])

        if no == "2":
            value = _getDictVal(REFP,ned)
            try:
                result = currentValueShu * thickness_Specified * coeff / float(value)
                self.Logger.info("For Shu no.{}- Thickness at reference point is {}".format(no, value))
                if result < 0:
                    self.Logger.error("The calculated current value was negative... Check EPPS server") 
                    result = None
            except ZeroDivisionError:
                self.Logger.error("Thickness at reference point was zero")
                result = None

        elif no == "3":
            value = _getDictVal(AVGDS,ned)
            try:
                result = currentValueShu * thickness_Specified * coeff / float(_getDictVal(AVGDS,ned))
                self.Logger.info("For Shu no.{}- Avg DS thickness {}".format(no, value))
                if result < 0:
                    self.Logger.error("The calculated current value was negative... Check EPPS server")
                    result = None
            except ZeroDivisionError:
                self.Logger.error("Zero average thickness...")
                result = None

        elif no == "4":
            ds_nodeId, max_ds_thickNess = _getDictVal(MAXDS,ned)
            pl_nodeId, max_pl_thickness = _getDictVal(MAXPL,ned)
            try:
                ds_coeff = thickness_Upper_Threshold_DS * coeff/float(max_ds_thickNess)
                pl_coeff = thickness_Upper_Threshold_PL * coeff/float(max_pl_thickness)
                self.Logger.info("For Shu no.{}- found maxDsThickness {} at node id {} and maxPlThickness {} at node id {}".format(no, max_ds_thickNess, ds_nodeId, max_pl_thickness, pl_nodeId))
                result = currentValueShu * min(ds_coeff, pl_coeff)
                if result < 0:
                    self.Logger.error("The calculated current value was negative... Check EPPS server")
                    result = None
            except ZeroDivisionError:
                self.Logger.error("Max thickness either DS or PL was found to be zero at {}, {} respectively".format(ds_nodeId, pl_nodeId))
                result = None
        
        elif no == "5":
            ds_nodeId, min_ds_thickness = _getDictVal(MINDS,ned)
            try:
                ds_coeff = thickness_Lower_Threshold * coeff / float(min_ds_thickness)
                result = currentValueShu * ds_coeff
                self.Logger.info("For Shu no.{}- found minDSThickness {} at node id {}".format(no, min_ds_thickness, ds_nodeId))
                if result < 0:
                    nodeId, minThickness = _getDictVal(MINPOSDS, ned)
                    self.Logger.info("The calculated current value was negative. re-calculate with minimum positive thickness {} at node id {}".format(minThickness, nodeId))
                    result = currentValueShu * thickness_Lower_Threshold  * coeff / float(minThickness)
            except ZeroDivisionError:
                self.Logger.info("Minimum thickness was found to be zero at node id {}".format(ds_nodeId))
                nodeId, minThickness = _getDictVal(MINPOSDS, ned)
                self.Logger.info("re-calculated with minimum positive thickness {} at node id {}".format(minThickness, nodeId))
                result = currentValueShu * thickness_Lower_Threshold  * coeff / float(minThickness)
        return result

    def getNewCurrentValForHozo(self, no, md, ned):
        self.Logger.info("Calculating new current value for the Hojyo type {}".format(no))
        result = None
        if no == "7":
            _, current = _getDictVal(MAXMT,ned)
            self.Logger.info("The calculated current value is {}".format(current))
            if current > 0:
                result = current                
            else:
                self.Logger.info("Set 1e-9 for the new current instead")
                result = 1e-9
        return result

        #     nodeId, thickness = _getDictVal(MINMT,ned)
        #     try:
        #         result = currentValueShu * thickness_Lower_Threshold * coeff / float(thickness)
        #         self.Logger.info("For hojyo - found minimum_thickness {} at node id {}".format(thickness, nodeId))
        #         if result < 0:
        #             nodeId, minThickness = _getDictVal(MINPOSMT, ned)
        #             self.Logger.info("The calculated current value was negative. Instead, used minimum positive thickness {} at node id {}".format(minThickness, nodeId))
        #             result = currentValueShu * thickness_Lower_Threshold  * coeff / float(minThickness)
        #     except ZeroDivisionError:
        #         self.Logger.info("Minimum thickness was found to be zero at node id {}".format(nodeId))
        #         nodeId, minThickness = _getDictVal(MINPOSMT, ned)
        #         self.Logger.info("re-calculated with minimum positive thickness {} at node id {}".format(minThickness, nodeId))
        #         result = currentValueShu * thickness_Lower_Threshold  * coeff / float(minThickness)            
        # return result
    
    def exportNewInputCurrent(self, fPath, shuVal, hozoVal, rimenVal):
        with open(fPath, "w") as f_writer:
            f_writer.write("{},{},{}\n".format(shuVal, hozoVal, rimenVal))        
    
    def toFile(self, neu1path, neu2path, md, newVal):
        if newVal == REN:
            self.Logger.info("Renaming {} to {}".format(neu1path, neu2path))
            os.rename(neu1path, neu2path)
        else:
            self.Logger.info("Creating {} with newVal {}".format(neu2path, newVal))

            E12 = md["E012"]
            E13 = md["E013"]
            E15 = md["E015"]
            E16 = md["E016"]
            
            with open(neu2path, "w") as f_write:
                with open(neu1path, "r") as f_read:
                    self.Logger.info("Reading {}".format(neu1path))
                    counter = 0
                    for line in f_read:
                        line = line.rstrip()
                        if counter == 27:
                            f_write.write("{},{},{},{},{}\n".format(E12, E13, newVal, E15, E16))
                        else:
                            f_write.write("{}\n".format(line))
                        counter += 1
            self.Logger.info("Deleting {}".format(neu1path))
            os.remove(neu1path)
        
    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.info("No such file or directory : {}".format(f_name))
            return False
        return True
    
    def createinputFileText(self, neuName):
        if neuName == self.NEU2_MAIN_INPUT:
            neufileTXT = self.NEUSHU2
            fmofileTXT = self.FMOSHU2
        elif neuName == self.NEU2_HOZO_INPUT:
            neufileTXT = self.NEUHOZO2
            fmofileTXT = self.FMOHOZO2
        elif neuName == self.NEU3_HOZO_INPUT:
            neufileTXT = self.NEUHOZO3
            fmofileTXT = self.FMOHOZO3

        with open(neufileTXT, "w") as f:
            self.Logger.info("exporting {}".format(neufileTXT))
            f.write(neuName)
            
        with open(fmofileTXT, "w") as f:
            self.Logger.info("exporting {}".format(fmofileTXT))
            fmo = "{}.fmo".format(neuName.split(".")[0])
            lineLst = ["6400000","0", fmo, "1", "0", "0.001", "1"]
            f.write('\n'.join(lineLst))
            

def _getDictVal(the_key, d):
    for key in d:
        if the_key in key:
            return d[key]


