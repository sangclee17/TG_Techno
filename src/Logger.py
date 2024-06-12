import os
from datetime import datetime

class Logger():
    def __init__(self, workingFolderNm, fileDir):
        self.__fileDir = fileDir
        self.__workingFolderNm = workingFolderNm

    def info(self, status):
        self.logging("INFO", self.__fileDir, self.__workingFolderNm, status)

    def error(self, status):
        self.logging("ERROR", self.__fileDir, self.__workingFolderNm, status)
        
    def writeToFile(self, fname, lineLst):
        with open(fname, "a") as f:
            f.write('\n'.join(lineLst))

    def logging(self, logType, fDir, fName, status):
        now = datetime.now()
        if not fName:
            line = "{:02}月{:02}日 {:02}:{:02}:{:02} [{}] {}\n".format(int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second), logType, status)
        else:
            line = "{:02}月{:02}日 {:02}:{:02}:{:02} フォルダ:{} [{}] {}\n".format(int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second), fName, logType, status)
        self.writeToFile(fDir, [line])