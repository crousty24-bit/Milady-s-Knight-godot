@echo off
setlocal
set /p "GODOT_VERSION="<"%~dp0tools\godot-version.txt"
if not defined GODOT_EXE set "GODOT_EXE=%USERPROFILE%\OneDrive\Documents\Godot Engine\Godot_v%GODOT_VERSION%-stable_win64.exe"
if not exist "%GODOT_EXE%" (
  echo Godot %GODOT_VERSION% introuvable. Definir GODOT_EXE avec le chemin de son executable.
  exit /b 1
)
set "DETECTED_VERSION="
for /f "delims=" %%V in ('""%GODOT_EXE%" --version"') do set "DETECTED_VERSION=%%V"
echo %DETECTED_VERSION%| findstr /b /l /c:"%GODOT_VERSION%.stable." >nul
if errorlevel 1 (
  echo Godot %GODOT_VERSION% stable requis, version detectee : %DETECTED_VERSION%
  exit /b 1
)
"%GODOT_EXE%" --path "%~dp0." %*
exit /b %errorlevel%
