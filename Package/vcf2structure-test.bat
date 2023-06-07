@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program vcf2structure.py
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

rem Run the program vcf2structure.py

%PYTHON% %PYTHON_OPTIONS% vcf2structure.py ^
    --vcf=%DATA_DIR%\concatenated_imputed_progenies-6000DP-scenario2.vcf ^
    --samples=%DATA_DIR%\IDs-total.txt ^
    --sp1_id=AL ^
    --sp2_id=EN ^
    --hyb_id=HY ^
    --new_mdi=-109 ^
    --imd_id=99 ^
    --trans=ADD100 ^
    --out=%OUTPUT_DIR%\concatenated_imputed_progenies-6000DP-scenario2-structure.tsv ^
    --format=2 ^
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
