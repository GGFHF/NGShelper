@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program get-exon-data-wchim.py
rem in a Windows environment.
rem
rem This software has been developed by:
rem
rem     GI en especies leñosas (WooSp)
rem     Dpto. Sistemas y Recursos Naturales
rem     ETSI Montes, Forestal y del Medio Natural
rem     Universidad Politecnica de Madrid
rem     https://github.com/ggfhf/
rem
rem Licence: GNU General Public Licence Version 3.

rem ----------------------------------------------------------------------------

rem Control parameters

if not "%*" == "" (set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

rem Set environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHON=python.exe
set PYTHON_OPTIONS=
set PYTHONPATH=.

set NGSHELPER_DIR=%NGSHELPER%
set DATA_DIR=%NGSHELPER%\data
set OUTPUT_DIR=%NGSHELPER%\output

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

set INITIAL_DIR=%cd%
cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Run the program get-exon-data-wchim.py

%PYTHON% %PYTHON_OPTIONS% get-exon-data-wchim.py ^
    --alignment=%DATA_DIR%\alignment.log.gz ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

rem ----------------------------------------------------------------------------

:END

cd %INITIAL_DIR%

if %ERROR% equ 0 (
    rem -- exit 0
)

if %ERROR% equ 1 (
    echo *** ERROR: This script does not have input parameters.
    rem -- pause
    rem -- exit %RC%
)

if %ERROR% equ 2 (
    echo *** ERROR: The program ended with return code %RC%.
    rem -- pause
    rem -- exit %RC%
)

rem ----------------------------------------------------------------------------