@echo off

rem ----------------------------------------------------------------------------

rem This script runs the program filter-ssrs.py in a Windows environment.
rem
rem This software has been developed by:
rem
rem     Dpto. Sistemas y Recursos Naturales
rem     ETSI Montes, Forestal y del Medio Natural
rem     Universidad Politecnica de Madrid
rem     https://github.com/ggfhf/
rem
rem Licence: GNU General Public Licence Version 3.

rem ----------------------------------------------------------------------------

rem Control parameters

rem if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHON=python.exe
set PYTHON_OPTIONS=
set ARGV=
set PYTHONPATH=.

set NGSHELPER_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper"

cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Execute the program filter-ssrs.py

:TRANSCRIPT_FILTER

%PYTHON% %PYTHON_OPTIONS% filter-ssrs.py %* %ARGV%
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
