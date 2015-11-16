@echo off
set PYTHONPATH=%~dp0\..;%PYTHONPATH%
"c:\Program Files (x86)\python34\python.exe" -m ht3 -s %~dp0\..\scripts %*
