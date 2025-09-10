@echo off
REM Change to script directory
cd /d %~dp0

REM Clean previous build/dist if exist
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist GUI.spec del GUI.spec

REM Build the GUI app with icon
pyinstaller ^
    GUI.py ^
    --noconfirm ^
    --onefile ^
    --icon="..\assets\bip-icon.ico" ^
    --name "BayerImageProcessor" ^
    --add-data "..\assets\bip-icon.ico;assets"
REM --windowed

REM Check if build succeeded
if exist dist\GUI.exe (
	echo Build succeeded! Find your executable in dist\GUI.exe
) else (
	echo Build failed. Check the output above for errors.
)