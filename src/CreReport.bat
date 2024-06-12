@echo off

rem ---------------------
rem This batch file is supposed to be called from each folder in COMMON folder.
rem ---------------------

rem If there is no syu-analysis result, a report is not created.
if not exist Premodel3.nez (
  goto end
)

rem ---------------------
rem Reads setting file.
rem ---------------------
for /f "usebackq tokens=1-2 delims=," %%a in (..\..\sys_config.csv) do (set %%a=%%b)

rem ---------------------
rem Creates master h3d file by using analysis-result.
rem ---------------------
call "%HYPER_MESH_PATH%" -tcl ..\..\..\src\hm_Creh3d.tcl
if exist Errorflg (
  goto end
)

rem ---------------------
rem Creates image files and h3d files for report.
rem ---------------------
call "%HYPER_VIEW_PATH%" -b -tcl ..\..\..\src\hv_Cremodel.tcl
if exist Errorflg (
  goto end
)

rem ---------------------
rem Creates a report.
rem Copies and executes, because location of excel file is working folder in VBA script.
rem ---------------------
call "%EXCEL_PATH%" ..\..\..\src\template.xlsm

:end
exit