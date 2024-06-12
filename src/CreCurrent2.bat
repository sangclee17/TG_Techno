@echo off

for /f "usebackq tokens=1-2 delims=," %%a in (..\..\sys_config.csv) do (set %%a=%%b)
set WORKING_FOLDER_DIR=%cd%

call "%SL_PATH%" -auto "..\..\..\src\PreAuto3.py" "%WORKING_FOLDER_DIR%"
exit