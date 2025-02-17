@echo off

rem ----------------------------------------------------------------------------

rem This script runs the program get-transcripts-geneid.py in a Windows environment.
rem
rem This software has been developed by:
rem
rem     GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
rem     Dpto. Sistemas y Recursos Naturales
rem     ETSI Montes, Forestal y del Medio Natural
rem     Universidad Politecnica de Madrid
rem     https://github.com/ggfhf/
rem
rem Licence: GNU General Public Licence Version 3.

rem ----------------------------------------------------------------------------

rem Set environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHON=python.exe
set PYTHON_OPTIONS=
set ARGV=
set PYTHONPATH=.

set NGSHELPER_DIR=%NGSHELPER%

set INITIAL_DIR=%cd%
cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Run the program get-transcripts-geneid.py

%PYTHON% %PYTHON_OPTIONS% get-transcripts-geneid.py %* %ARGV%
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

:END

cd %INITIAL_DIR%

if %ERROR% equ 0 (
    rem -- exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: The program ended with return code %RC%.
    rem -- pause
    rem -- exit %RC%
)

rem ----------------------------------------------------------------------------
