@echo off
cd /D %~dp0
"c:\Program Files (x86)\python34\python.exe" -m ht3.cli -s scripts/ -x "show('Hello World')" -i -x "show('Bye World')"
