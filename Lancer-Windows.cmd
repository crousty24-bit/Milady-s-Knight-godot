@echo off
setlocal
if not defined GODOT_EXE set "GODOT_EXE=C:\Users\allen\OneDrive\Documents\Godot Engine\Godot_v4.5.1-stable_win64.exe"
if not exist "%GODOT_EXE%" (
  echo Godot introuvable. Definir GODOT_EXE ou importer project.godot dans Godot 4.5.1.
  pause
  exit /b 1
)
"%GODOT_EXE%" --path "%~dp0." %*
