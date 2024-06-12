from hwx import simlab
import subprocess
import os
import shutil
import csv
from datetime import datetime
from Logger import Logger

class Sys_Utility():
    def __init__(self, folderNm, logDir):
        self.Logger = Logger(folderNm, logDir)
    
    def readAnalysisCondition(self, condDir):
        if not self.fileExists(condDir):return None
        modelCondDict = {}
        with open(condDir,'r') as f:
            lines = f.readlines()
            for line in lines:
                lineSp = line.split(':')
                if len(lineSp) >= 2:
                    frtCut = lineSp[0]
                    rearCut = lineSp[1]
                    if frtCut == "A001":modelCondDict["A001"] = rearCut
                    elif frtCut == "A002":modelCondDict["A002"] = rearCut
                    elif frtCut == "A003":modelCondDict["A003"] = rearCut
                    elif frtCut == "A004":modelCondDict["A004"] = rearCut
                    elif frtCut == "A005":modelCondDict["A005"] = rearCut
                    elif frtCut == "A006":modelCondDict["A006"] = rearCut
                    elif frtCut == "A007":modelCondDict["A007"] = rearCut
                    elif frtCut == "A008":modelCondDict["A008"] = rearCut
                    elif frtCut == "A009":modelCondDict["A009"] = rearCut
                    elif frtCut == "A010":modelCondDict["A010"] = rearCut
                    elif frtCut == "A011":modelCondDict["A011"] = rearCut
                    elif frtCut == "A012":modelCondDict["A012"] = rearCut
                    elif frtCut == "A013":modelCondDict["A013"] = rearCut
                    elif frtCut == "A014":modelCondDict["A014"] = rearCut
                    elif frtCut == "A015":modelCondDict["A015"] = rearCut
                    elif frtCut == "A016":modelCondDict["A016"] = rearCut
                    elif frtCut == "A017":modelCondDict["A017"] = rearCut
                    elif frtCut == "A018":modelCondDict["A018"] = rearCut
                    elif frtCut == "A019":modelCondDict["A019"] = rearCut
                    elif frtCut == "A020":modelCondDict["A020"] = rearCut
                    elif frtCut == "A021":modelCondDict["A021"] = rearCut
                    elif frtCut == "A022":modelCondDict["A022"] = rearCut
                    elif frtCut == "A023":modelCondDict["A023"] = rearCut
                    elif frtCut == "A024":modelCondDict["A024"] = rearCut
                    elif frtCut == "A025":modelCondDict["A025"] = rearCut
                    elif frtCut == "A026":modelCondDict["A026"] = rearCut
                    elif frtCut == "A027":modelCondDict["A027"] = rearCut
                    elif frtCut == "A028":modelCondDict["A028"] = rearCut
                    elif frtCut == "A029":modelCondDict["A029"] = rearCut
                    elif frtCut == "A030":modelCondDict["A030"] = rearCut
                    elif frtCut == "A031":modelCondDict["A031"] = rearCut
                    elif frtCut == "A032":modelCondDict["A032"] = rearCut
                    elif frtCut == "A033":modelCondDict["A033"] = rearCut
                    elif frtCut == "A034":modelCondDict["A034"] = rearCut
                    elif frtCut == "A035":modelCondDict["A035"] = rearCut
                    elif frtCut == "A036":modelCondDict["A036"] = rearCut
                    elif frtCut == "A037":modelCondDict["A037"] = rearCut
                    elif frtCut == "A038":modelCondDict["A038"] = rearCut
                    elif frtCut == "A039":modelCondDict["A039"] = rearCut
                    elif frtCut == "A040":modelCondDict["A040"] = rearCut
                    elif frtCut == "A041":modelCondDict["A041"] = rearCut
                    elif frtCut == "A042":modelCondDict["A042"] = rearCut
                    elif frtCut == "A043":modelCondDict["A043"] = rearCut
                    elif frtCut == "A044":modelCondDict["A044"] = rearCut
                    elif frtCut == "A045":modelCondDict["A045"] = rearCut
                    elif frtCut == "A046":modelCondDict["A046"] = rearCut
                    elif frtCut == "A047":modelCondDict["A047"] = rearCut
                    elif frtCut == "A048":modelCondDict["A048"] = rearCut
                    elif frtCut == "A049":modelCondDict["A049"] = rearCut
                    elif frtCut == "A050":modelCondDict["A050"] = rearCut
                    elif frtCut == "A051":modelCondDict["A051"] = rearCut
                    elif frtCut == "A052":modelCondDict["A052"] = rearCut
                    elif frtCut == "A053":modelCondDict["A053"] = rearCut
                    elif frtCut == "A054":modelCondDict["A054"] = rearCut
                    elif frtCut == "A055":modelCondDict["A055"] = rearCut
                    elif frtCut == "A056":modelCondDict["A056"] = rearCut
                    elif frtCut == "A057":modelCondDict["A057"] = rearCut
                    elif frtCut == "A058":modelCondDict["A058"] = rearCut
                    elif frtCut == "A059":modelCondDict["A059"] = rearCut
                    elif frtCut == "A060":modelCondDict["A060"] = rearCut
                    elif frtCut == "A061":modelCondDict["A061"] = rearCut
                    elif frtCut == "A062":modelCondDict["A062"] = rearCut
                    elif frtCut == "A063":modelCondDict["A063"] = rearCut
                    elif frtCut == "A064":modelCondDict["A064"] = rearCut
                    elif frtCut == "A065":modelCondDict["A065"] = rearCut
                    elif frtCut == "A066":modelCondDict["A066"] = rearCut
                    elif frtCut == "A067":modelCondDict["A067"] = rearCut
                    elif frtCut == "A068":modelCondDict["A068"] = rearCut
                    elif frtCut == "A069":modelCondDict["A069"] = rearCut
                    elif frtCut == "A070":modelCondDict["A070"] = rearCut
                    elif frtCut == "A071":modelCondDict["A071"] = rearCut
                    elif frtCut == "A072":modelCondDict["A072"] = rearCut
                    elif frtCut == "A073":modelCondDict["A073"] = rearCut
                    elif frtCut == "A074":modelCondDict["A074"] = rearCut
                    elif frtCut == "A075":modelCondDict["A075"] = rearCut
                    elif frtCut == "A076":modelCondDict["A076"] = rearCut
                    elif frtCut == "A077":modelCondDict["A077"] = rearCut
                    elif frtCut == "A078":modelCondDict["A078"] = rearCut
                    elif frtCut == "A079":modelCondDict["A079"] = rearCut
                    elif frtCut == "A080":modelCondDict["A080"] = rearCut
                    elif frtCut == "A081":modelCondDict["A081"] = rearCut
                    elif frtCut == "A082":modelCondDict["A082"] = rearCut
                    elif frtCut == "A083":modelCondDict["A083"] = rearCut
                    elif frtCut == "A084":modelCondDict["A084"] = rearCut
                    elif frtCut == "B001":modelCondDict["B001"] = rearCut
                    elif frtCut == "B002":modelCondDict["B002"] = rearCut
                    elif frtCut == "B003":modelCondDict["B003"] = rearCut
                    elif frtCut == "B004":modelCondDict["B004"] = rearCut
                    elif frtCut == "B005":modelCondDict["B005"] = rearCut
                    elif frtCut == "B006":modelCondDict["B006"] = rearCut
                    elif frtCut == "B007":modelCondDict["B007"] = rearCut
                    elif frtCut == "C001":modelCondDict["C001"] = rearCut
                    elif frtCut == "C002":modelCondDict["C002"] = rearCut
                    elif frtCut == "C003":modelCondDict["C003"] = rearCut
                    elif frtCut == "C004":modelCondDict["C004"] = rearCut
                    elif frtCut == "C005":modelCondDict["C005"] = rearCut
                    elif frtCut == "C006":modelCondDict["C006"] = rearCut
                    elif frtCut == "C007":modelCondDict["C007"] = rearCut
                    elif frtCut == "C008":modelCondDict["C008"] = rearCut
                    elif frtCut == "C009":modelCondDict["C009"] = rearCut
                    elif frtCut == "C010":modelCondDict["C010"] = rearCut
                    elif frtCut == "C011":modelCondDict["C011"] = rearCut
                    elif frtCut == "C012":modelCondDict["C012"] = rearCut
                    elif frtCut == "C013":modelCondDict["C013"] = rearCut
                    elif frtCut == "C014":modelCondDict["C014"] = rearCut
                    elif frtCut == "C015":modelCondDict["C015"] = rearCut
                    elif frtCut == "D001":modelCondDict["D001"] = rearCut
                    elif frtCut == "D002":modelCondDict["D002"] = rearCut
                    elif frtCut == "D003":modelCondDict["D003"] = rearCut
                    elif frtCut == "D004":modelCondDict["D004"] = rearCut
                    elif frtCut == "D005":modelCondDict["D005"] = rearCut
                    elif frtCut == "D006":modelCondDict["D006"] = rearCut
                    elif frtCut == "E001":modelCondDict["E001"] = rearCut
                    elif frtCut == "E002":modelCondDict["E002"] = rearCut
                    elif frtCut == "E003":modelCondDict["E003"] = rearCut
                    elif frtCut == "E004":modelCondDict["E004"] = rearCut
                    elif frtCut == "E005":modelCondDict["E005"] = rearCut
                    elif frtCut == "E006":modelCondDict["E006"] = rearCut
                    elif frtCut == "E007":modelCondDict["E007"] = rearCut
                    elif frtCut == "E008":modelCondDict["E008"] = rearCut
                    elif frtCut == "E009":modelCondDict["E009"] = rearCut
                    elif frtCut == "E010":modelCondDict["E010"] = rearCut
                    elif frtCut == "E011":modelCondDict["E011"] = rearCut
                    elif frtCut == "E012":modelCondDict["E012"] = rearCut
                    elif frtCut == "E013":modelCondDict["E013"] = rearCut
                    elif frtCut == "E014":modelCondDict["E014"] = rearCut
                    elif frtCut == "E015":modelCondDict["E015"] = rearCut
                    elif frtCut == "E016":modelCondDict["E016"] = rearCut
                    elif frtCut == "E017":modelCondDict["E017"] = rearCut
                    elif frtCut == "E018":modelCondDict["E018"] = rearCut
                    elif frtCut == "E019":modelCondDict["E019"] = rearCut
                    elif frtCut == "E020":modelCondDict["E020"] = rearCut
                    elif frtCut == "E021":modelCondDict["E021"] = rearCut
                    elif frtCut == "E022":modelCondDict["E022"] = rearCut
                    elif frtCut == "E023":modelCondDict["E023"] = rearCut
                    elif frtCut == "E024":modelCondDict["E024"] = rearCut
                    elif frtCut == "E025":modelCondDict["E025"] = rearCut
                    elif frtCut == "E026":modelCondDict["E026"] = rearCut
                    elif frtCut == "E027":modelCondDict["E027"] = rearCut
                    elif frtCut == "E028":modelCondDict["E028"] = rearCut
                    elif frtCut == "E029":modelCondDict["E029"] = rearCut
                    elif frtCut == "E030":modelCondDict["E030"] = rearCut
                    elif frtCut == "E031":modelCondDict["E031"] = rearCut
                    elif frtCut == "E032":modelCondDict["E032"] = rearCut
                    elif frtCut == "E033":modelCondDict["E033"] = rearCut
                    elif frtCut == "E034":modelCondDict["E034"] = rearCut
                    elif frtCut == "E035":modelCondDict["E035"] = rearCut
                    elif frtCut == "E036":modelCondDict["E036"] = rearCut
                    elif frtCut == "E037":modelCondDict["E037"] = rearCut
                    elif frtCut == "E038":modelCondDict["E038"] = rearCut
                    elif frtCut == "E039":modelCondDict["E039"] = rearCut
                    elif frtCut == "E040":modelCondDict["E040"] = rearCut
                    elif frtCut == "E041":modelCondDict["E041"] = rearCut
                    elif frtCut == "E042":modelCondDict["E042"] = rearCut
                    elif frtCut == "E043":modelCondDict["E043"] = rearCut
                    elif frtCut == "E044":modelCondDict["E044"] = rearCut
                    elif frtCut == "E045":modelCondDict["E045"] = rearCut
                    elif frtCut == "E046":modelCondDict["E046"] = rearCut
                    elif frtCut == "E047":modelCondDict["E047"] = rearCut
                    elif frtCut == "E048":modelCondDict["E048"] = rearCut
                    elif frtCut == "E049":modelCondDict["E049"] = rearCut
                    elif frtCut == "E050":modelCondDict["E050"] = rearCut
                    elif frtCut == "E051":modelCondDict["E051"] = rearCut
                    elif frtCut == "E052":modelCondDict["E052"] = rearCut
                    elif frtCut == "E053":modelCondDict["E053"] = rearCut
                    elif frtCut == "E054":modelCondDict["E054"] = rearCut
                    elif frtCut == "E055":modelCondDict["E055"] = rearCut
                    elif frtCut == "E056":modelCondDict["E056"] = rearCut
                    elif frtCut == "E057":modelCondDict["E057"] = rearCut
                    elif frtCut == "E058":modelCondDict["E058"] = rearCut
                    elif frtCut == "E059":modelCondDict["E059"] = rearCut
                    elif frtCut == "E060":modelCondDict["E060"] = rearCut
                    elif frtCut == "E061":modelCondDict["E061"] = rearCut
                    elif frtCut == "E062":modelCondDict["E062"] = rearCut
                    elif frtCut == "E063":modelCondDict["E063"] = rearCut
                    elif frtCut == "E064":modelCondDict["E064"] = rearCut
                    elif frtCut == "F001":modelCondDict["F001"] = rearCut
                    elif frtCut == "F002":modelCondDict["F002"] = rearCut
                    elif frtCut == "F003":modelCondDict["F003"] = rearCut
                    elif frtCut == "F004":modelCondDict["F004"] = rearCut
                    elif frtCut == "F005":modelCondDict["F005"] = rearCut
                    elif frtCut == "F006":modelCondDict["F006"] = rearCut
                    elif frtCut == "Z001":modelCondDict["Z001"] = rearCut
        return modelCondDict

    def fileExists(self, f_name):
        if not os.path.exists(f_name):
            self.Logger.error("No such file or directory : {}".format(f_name))
            return False
        return True
    
    def exportKomPath(self, cond_dict):
        try:
            year = cond_dict["A081"]
            series = cond_dict["A001"]
            prodNm = cond_dict["A002"]
            grade = cond_dict["A004"]
            phase = cond_dict["A005"]
            suiji = cond_dict["A080"]
        except KeyError as e:
            self.Logger.error("No such paprameter, {} from analysis conditions txt !!".format(e))
        else:
            with open("kom.txt", "w") as f:
                f.write("{}/{}/{}/{}/{}/{}\n".format(year, series, prodNm, grade, phase, suiji))

def writeToFile(fname, append_write, lineLst):
    with open(fname, append_write) as f:
        f.write('\n'.join(lineLst))


