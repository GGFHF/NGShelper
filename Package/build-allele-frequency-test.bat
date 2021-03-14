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

rem This script executes a test of the program build-allele-frequency.py
rem in a Windows environment.

rem ----------------------------------------------------------------------------

rem Control parameters

if not "%*" == "" (set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set ERROR=0

set PYTHONPATH=.
set PYTHON_OPTIONS=

set NGSHELPER_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper"
set DATA_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper\data"
set OUTPUT_DIR="C:\Users\FMM\Documents\ProyectosVS\NGShelper\NGShelper\output"

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Execute the program build-allele-frequency.py

rem python.exe %PYTHON_OPTIONS% build-allele-frequency.py ^
rem     --vcf=%DATA_DIR%\concatenated_imputed_progenies-6000DP-scenario2.vcf ^
rem     --samples=%DATA_DIR%\IDs-total.txt ^
rem     --sp1_id=AL ^
rem     --sp2_id=EN ^
rem     --hyb_id=HY ^
rem     --outdir=%OUTPUT_DIR% ^
rem     --varnum=1000 ^
rem     --trans=ADD100 ^
rem     --verbose=Y ^
rem     --trace=N ^
rem     --tvi=NONE
rem if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

python.exe %PYTHON_OPTIONS% build-allele-frequency.py ^
    --vcf=%DATA_DIR%\Selected-for-simhyb.recode.vcf ^
    --samples=%DATA_DIR%\keep-adults-simhyb.txt ^
    --sp1_id=AL ^
    --sp2_id=EN ^
    --hyb_id=NONE ^
    --outdir=%OUTPUT_DIR% ^
    --varnum=1000 ^
    --trans=ATCG ^
    --verbose=N ^
    --trace=Y ^
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
