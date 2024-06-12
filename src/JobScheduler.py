
import sys
import os
import shutil
import time
from distutils import dir_util
import subprocess
import re

def main():
    SRC_DIR = os.path.dirname(__file__)
    PROJ_DIR = os.path.join(SRC_DIR, "..", "project")
    os.chdir(PROJ_DIR)

    SERVER_PATH = ""
    with open("sys_config.csv", "r") as f:
        for line in f:
            lineSp = line.rstrip().split(",")
            if lineSp[0] == "SERVER_PATH":SERVER_PATH = lineSp[1]
    if not SERVER_PATH: return
    PROJ_COMMON = os.path.abspath(os.path.join(PROJ_DIR, "COMMON"))

    while True:
        folderNms = getFolderList(SERVER_PATH) 
        for thisFolder in folderNms:
            thisDir = os.path.basename(thisFolder)

            # Only for folders names beginning with COMMON_
            if not thisDir.upper().startswith("COMMON_"):
                continue

            # Skip if user copy is not finished
            if not os.path.exists(os.path.join(thisFolder, "ENDOFCOPY.END")):
                continue

            jobDir_proj = os.path.join(PROJ_COMMON, thisDir)
            analysisTxt = getAnalysisConditonFile(thisFolder)
            if analysisTxt == None:
                continue

            # Copy the data. And make a copy of the analysis control file
            dir_util.copy_tree(thisFolder, jobDir_proj)
            shutil.copyfile(os.path.join(thisFolder, analysisTxt), os.path.join(jobDir_proj, "analysis_conditions.txt"))

            # Create a flag file that has been copied, and delete the original data from file-server
            with open(os.path.join(jobDir_proj,"ENDOFCOPY_SERVER.END"), "w") as f:
                pass
            shutil.rmtree(thisFolder)
        
        # Delete old joblist.txt
        if os.path.exists(os.path.join(SERVER_PATH, "JobList.txt")):os.remove(os.path.join(SERVER_PATH, "JobList.txt"))

        folderNms = getFolderList(PROJ_COMMON) 
        count = 1
        for thisFolder in folderNms:
            # Skip other than target
            if not os.path.basename(thisFolder).upper().startswith("COMMON_"):
                continue
            if not os.path.exists(os.path.join(thisFolder, "ENDOFCOPY.END")):
                continue
            if not os.path.exists(os.path.join(thisFolder, "ENDOFCOPY_SERVER.END")):
                continue
            if not os.path.exists(os.path.join(thisFolder, "analysis_conditions.txt")):
                continue

            # Write the waiting jobs to JobList.txt
            with open(os.path.join(SERVER_PATH, "JobList.txt"), "a") as f_write:
                with open(os.path.join(thisFolder,"analysis_conditions.txt"), "r") as f_read:
                    A001="";A002="";A062="";A063=""
                    for line in f_read:
                        linesp = line.split(":")
                        if linesp[0] == "A001": A001 = linesp[1].rstrip()
                        elif linesp[0] == "A002": A002 = linesp[1].rstrip()
                        elif linesp[0] == "A062": A062 = linesp[1].rstrip()
                        elif linesp[0] == "A063": A063 = linesp[1].rstrip()
                        if A001 and A002 and A062 and A063:
                            f_write.write("{}.{}/{}/{}/{}/{}\n".format(count, A001, A002, A062, A063,os.path.basename(thisFolder)))
                            break
            count+=1

        # SimLab pauses for 60 seconds to hold HWUnit license
        isAlive = sleepSimLab(60, 1)
        if not isAlive:
            sys.exit()

def getFolderList(fPath):
    fnms = [os.path.join(fPath, fn) for fn in os.listdir(fPath)]
    return sorted(fnms, key=os.path.getmtime)

def getAnalysisConditonFile(fPath):
    for thisFile in os.listdir(fPath):
        if not thisFile.lower().endswith(".txt"):
            continue

        # Search for a text file that contains the A001 key
        with open(os.path.join(fPath, thisFile), "r") as f_read:
            for line in f_read:
                linesp = line.split(":")
                if linesp[0] == "A001":
                    return thisFile
    return None

def isEPPSSchedulerAlive():
    cmd='for /F "usebackq tokens=2" %a in (`tasklist /fi "WINDOWTITLE eq EPPSScheduler*" ^| findstr "[0-9]"`) do @echo %a'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    isAlive = False
    for line in proc.stdout:
        if re.search("[0-9]",line.strip().decode('utf-8')):
            isAlive = True
            break
    return isAlive

def sleepSimLab(sleep_tile=60, interval_time=1):
    start_time = time.time()
    isAlive = True
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > sleep_tile:
            break
        if not isEPPSSchedulerAlive():
            isAlive = False
            break
        time.sleep(interval_time)

    return isAlive

if __name__ == "__main__":
    main()
