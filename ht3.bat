@echo off
cd /D %~dp0
"c:\Program Files (x86)\python34\python.exe" -m ht3.cli -s ht3.cfg -x "show('hans')" -i
