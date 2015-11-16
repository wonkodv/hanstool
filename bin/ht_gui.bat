@echo off
set PYTHONPATH=%~dp0\..;%PYTHONPATH%
"c:\Program Files (x86)\python34\python.exe" -m ht3 -f ht3.hotkey -f ht3.gui -s %~dp0\..\scripts %*
