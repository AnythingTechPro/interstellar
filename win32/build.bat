@echo off
cd ../
echo Compiling win32 executable...
C:/Python27/Scripts/nuitka.bat --verbose --standalone --python-version=2.7 --recurse-all --output-dir=distributable --enhanced --windows-disable-console --windows-icon=assets/icon.ico --msvc 10 interstellar/main.py
pause
