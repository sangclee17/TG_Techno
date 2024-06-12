@echo off

title EPPSScheduler
cd /d %~dp0

set config="sys_config.csv"
for /f "usebackq tokens=1-2 delims=," %%a in (%config%) do (
    if %%a==SL_PATH set sl_path=%%b
)

echo %date:~5,2%月%date:~8,2%日 %time:~0,2%:%time:~3,2%:%time:~6,2% コピープログラム実行中
call "%sl_path%" -auto ..\src\JobScheduler.py
