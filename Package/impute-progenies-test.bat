@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program impute-progenies.py
rem in a Windows environment.
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

if not "%*" == "" (set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

rem Set environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHON=python.exe
set PYTHON_OPTIONS=
set PYTHONPATH=.

set NGSHELPER_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper"
set DATA_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper\data"
set OUTPUT_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper\output"

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Run the program impute-progenies.py

%PYTHON% %PYTHON_OPTIONS% impute-progenies.py ^
    --vcf=%OUTPUT_DIR%\concatenated_imputed_adults-scenario2.vcf ^
    --samples=%DATA_DIR%\IDs-total.txt ^
    --scenario=2 ^
    --imd_id=99 ^
    --sp1_id=AL ^
    --sp2_id=EN ^
    --hyb_id=HY ^
    --out=%OUTPUT_DIR%\concatenated_imputed_progenies-scenario2.vcf ^
    --verbose=Y ^
    --trace=N ^
    --tvi=NONE
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

rem ----------------------------------------------------------------------------

:END

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
