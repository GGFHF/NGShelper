@echo off

rem ----------------------------------------------------------------------------

rem This software has been developed by:
rem
rem     GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
rem     Dpto. Sistemas y Recursos Naturales
rem     ETSI Montes, Forestal y del Medio Natural
rem     Universidad Politecnica de Madrid
rem     https://github.com/ggfhf/
rem
rem Licence: GNU General Public Licence Version 3.

rem ----------------------------------------------------------------------------

rem This program launches several PHASE processes with a input file list.

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHONPATH=.
set PYTHON_OPTIONS=
set ARGV=

set NGSHELPER_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper"

cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Execute the program launch-phase-processes.py

python.exe %PYTHON_OPTIONS% launch-phase-processes.py %* %ARGV%
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

:END

if %ERROR% equ 0 (
    rem -- exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: The program ended with return code %RC%.
    rem -- pause
    rem -- exit %RC%
)

rem ----------------------------------------------------------------------------
