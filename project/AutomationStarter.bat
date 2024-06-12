@echo off
setlocal enabledelayedexpansion

title AutoEPPS
cd /d %~dp0

rem local parameters
set PROJ_DIR=%cd%
set joblist="JobList.txt"
set result="result"
set original="original"
set config="sys_config.csv"
set autolog="AutoLog.txt"
set komPath="kom.txt"
set kekkaFold="?��?��͌�?��?��"
set SRC_DIR=%PROJ_DIR%\..\src
set WORKING_FOLDER_NAME=WORKING_FOLDER

set neushu1="neu_shu1.txt"
set fmoshu1="fmo_shu1.txt"
set neuhozo1="neu_hozo1.txt"
set fmohozo1="fmo_hozo1.txt"
set neuback1="neu_back1.txt"
set fmoback1="fmo_back1.txt"
set neushu2="neu_shu2.txt"
set fmoshu2="fmo_shu2.txt"
set neuhozo2="neu_hozo2.txt"
set fmohozo2="fmo_hozo2.txt"
set neuback2="neu_back2.txt"
set fmoback2="fmo_back2.txt"
set neuhozo3="neu_hozo3.txt"
set fmohozo3="fmo_hozo3.txt"

rem Read cnfig
for /f "usebackq tokens=1-2 delims=," %%a in (%config%) do (
    if %%a==SL_PATH set sl_path=%%b
    if %%a==EPPS_FEMAPAC_EXE set EPPS_FEMAPAC=%%b
    if %%a==EPPS_ASTEAN_EXE set EPPS_ASTEAN=%%b
    if %%a==SERVER_PATH set serv_path=%%b
    if %%a==RESULT_PATH set result_path=%%b
    if %%a==ERROR_PATH set error_path=%%b
)

rem Automation Start
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��?��?��?��?��?��?��v?��?��?��O?��?��?��?��?��J?��n
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��?��?��?��?��?��?��v?��?��?��O?��?��?��?��?��J?��n>"%PROJ_DIR%\%autolog%"

rem Initialize (deletes old data and log)
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��?��?��?��?��?��
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��?��?��?��?��?��>>"%PROJ_DIR%\%autolog%"
if exist .\COMMON\COMMON* for /f %%a in ('dir /b .\COMMON\COMMON*') do (rd /s /q .\COMMON\%%a)
if exist "%serv_path%\%joblist%" (del "%serv_path%\%joblist%">nul)
if exist "%serv_path%\%autolog%" (del "%serv_path%\%autolog%">nul)

rem ----- START LOOP ----- 
:spoint

rem If data folder is empty, skip.
if not exist .\COMMON\COMMON* (
    goto endloop
)
timeout 5 /nobreak >nul

set folderName=""
for /f %%a in ('dir /b /o:d /t:c .\COMMON\COMMON*') do (
    if exist .\COMMON\%%a\ENDOFCOPY_SERVER.END (
        set folderName=%%a
        goto ari
    )
)

if %folderName% == "" (
    goto endloop
)
:ari

rem Copy the data to workig folder
if exist .\COMMON\%WORKING_FOLDER_NAME% (rd /s /q .\COMMON\%WORKING_FOLDER_NAME%)
mkdir .\COMMON\%WORKING_FOLDER_NAME%
xcopy .\COMMON\"%folderName%"\* .\COMMON\%WORKING_FOLDER_NAME% /i /y >nul

rem Preprocess
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��f?��?��?��?��?��O?��J?��n
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��f?��?��?��?��?��O?��J?��n >>"%PROJ_DIR%\%autolog%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" %serv_path%>nul )
set WORKING_FOLDER_DIR=%PROJ_DIR%\COMMON\%WORKING_FOLDER_NAME%
call "%sl_path%" -auto "%SRC_DIR%\PreAuto1.py" "%WORKING_FOLDER_DIR%"
cd "%WORKING_FOLDER_DIR%"

if exist %neushu1% (
    if exist %fmoshu1% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?�� FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?�� FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neushu1%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?�� ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?�� ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmoshu1%
    )
)
if exist %neuhozo1% (
    if exist %fmohozo1% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?���? FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?���? FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neuhozo1%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?���? ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?���? ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmohozo1%
    )
)
if exist %neuback1% (
    if exist %fmoback1% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?��?��?�� FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?��?��?�� FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neuback1%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?��?��?�� ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 1st ?��?��?��?�� ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmoback1%
    )
)

echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��d?��?��?��l?��ύX
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��d?��?��?��l?��ύX >>"%PROJ_DIR%\%autolog%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" %serv_path%>nul )
start "?��d?��?��?��l?��ύX" /i /separate /wait "%SRC_DIR%\CreCurrent.bat"
cd "%WORKING_FOLDER_DIR%"

if exist %neushu2% (
    if exist %fmoshu2% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?�� FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?�� FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neushu2%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?�� ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?�� ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmoshu2%
    )
)
if exist %neuhozo2% (
    if exist %fmohozo2% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?���? FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?���? FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neuhozo2%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?���? ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?���? ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmohozo2%
    )
)
if exist %neuback2% (
    if exist %fmoback2% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?��?��?�� FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?��?��?�� FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neuback2%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?��?��?�� ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 2nd ?��?��?��?�� ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmoback2%
    )
)

echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��d?��?��?��l?��ύX
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��d?��?��?��l?��ύX >>"%PROJ_DIR%\%autolog%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" %serv_path%>nul )
start "?��d?��?��?��l?��ύX" /i /separate /wait "%SRC_DIR%\CreCurrent2.bat"
cd "%WORKING_FOLDER_DIR%"
if exist %neuhozo3% (
    if exist %fmohozo3% (
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 3rd ?���? FEMAPAC
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 3rd ?���? FEMAPAC >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_FEMAPAC%" < %neuhozo3%
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 3rd ?���? ASTEAN
        echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% 3rd ?���? ASTEAN >>"%PROJ_DIR%\%autolog%"
        call "%EPPS_ASTEAN%" < %fmohozo3%
    )
)

rem Postprocess
cd "%WORKING_FOLDER_DIR%"
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��?��
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��?�� >>"%PROJ_DIR%\%autolog%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" %serv_path% >nul )
start "?��?��?��|?��[?��g?��?��" /i /separate /wait "%SRC_DIR%\CreReport.bat"

rem Export parameters
if not exist %komPath% (
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% Kom?��t?��@?��C?��?��?��?��?��?��?���?��?��܂�?��?��
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% Kom?��t?��@?��C?��?��?��?��?��?��?���?��?��܂�?��?��>>"%PROJ_DIR%\%autolog%"
    goto noresult
)
for /f "usebackq tokens=1-6 delims=/" %%a in (%komPath%) do (
    set year=%%a
    set series=%%b
    set prodNm=%%c
    set grade=%%d
    set phase=%%e
    set suiji=%%f
)

rem Output
if exist %result% (
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��I?��?�� ?��f?��[?��^?��?��?��R?��s?��[?��?��?��܂�
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��I?��?�� ?��f?��[?��^?��?��?��R?��s?��[?��?��?��܂�>>"%PROJ_DIR%\%autolog%"
    pushd "%result_path%" >nul
    if not exist "%year%" mkdir "%year%"
    cd "%year%"
    if not exist "%series%" mkdir "%series%"
    cd "%series%"
    if not exist "%prodNm%" mkdir "%prodNm%"
    cd "%prodNm%"
    if not exist "%grade%" mkdir "%grade%"
    cd "%grade%"
    if not exist "%folderName%_%phase%" mkdir "%folderName%_%phase%"
    cd "%folderName%_%phase%"
    if not exist %kekkaFold% mkdir %kekkaFold%
    if not exist "CAD" mkdir "CAD"
    cd %kekkaFold%
    popd >nul

    call xcopy "%WORKING_FOLDER_DIR%"\%result%\* "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\%kekkaFold% /i /y >nul
    call xcopy %PROJ_DIR%\COMMON\"%folderName%"\* "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\"CAD" /i /y >nul
    if exist "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\CAD\ENDOFCOPY_SERVER.END (
        del /q "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\CAD\ENDOFCOPY_SERVER.END
    )
    if exist "%WORKING_FOLDER_DIR%"\intersections_*.slb (
        call xcopy "%WORKING_FOLDER_DIR%"\intersections_*.slb "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\%kekkaFold% /i /y >nul
    )
    set A084=False
	for /f "tokens=1,2 delims=:" %%i in (%WORKING_FOLDER_DIR%\analysis_conditions.txt) do (set %%i=%%j>nul 2>&1)
    if !A084! == True (
        call xcopy "%WORKING_FOLDER_DIR%"\* "%result_path%"\"%year%"\"%series%"\"%prodNm%"\"%grade%"\"%folderName%_%phase%"\"CAD" /i /y /e >nul
    )
) else (
:noresult
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��?��?��s ?��f?��[?��^?��?��?��R?��s?��[?��?��?��܂�
    echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��|?��[?��g?��?��?��?��?��s ?��f?��[?��^?��?��?��R?��s?��[?��?��?��܂�>>"%PROJ_DIR%\%autolog%"
    pushd "%error_path%" >nul
    if not exist %folderName% mkdir %folderName%
    popd >nul
    xcopy "%WORKING_FOLDER_DIR%" "%error_path%\%folderName%" /i /y /e >nul
    copy "%PROJ_DIR%\%autolog%" "%error_path%\%folderName%" >nul
)

echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��?��?��?��?��?��?��?��?��I?��?��
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��t?��H?��?��?��_:%folderName% ?��?��?��?��?��?��?��?��?��?��?��I?��?��>>"%PROJ_DIR%\%autolog%"

rem Cleanup
cd "%PROJ_DIR%"
rd /s /q .\COMMON\"%folderName%" >nul
set folderName=""

rem ----- END LOOP ----- 
:endloop
cd "%PROJ_DIR%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" "%serv_path%">nul )
timeout 10 /nobreak >nul
goto spoint

rem Outside of loop. Process shouldn't come here.
:eof
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��\?��?��?��?��?��ʈُ킪?��?��?��?��?��?��?��܂�?��?�� ?��?��?��?��?��?��?��?��?��?��?��??�f?��?��?��܂�
echo %date:~5,2%?��?��%date:~8,2%?��?�� %time:~0,2%:%time:~3,2%:%time:~6,2% ?��\?��?��?��?��?��ʈُ킪?��?��?��?��?��?��?��܂�?��?�� ?��?��?��?��?��?��?��?��?��?��?��??�f?��?��?��܂� >>"%PROJ_DIR%\%autolog%"
if exist "%PROJ_DIR%\%autolog%" ( copy "%PROJ_DIR%\%autolog%" "%serv_path%">nul )
pause