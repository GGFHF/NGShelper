@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program calculate-enrichment-analysis.py
rem in a Windows environment.
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

rem Execute the program calculate-enrichment-analysis.py

%PYTHON% %PYTHON_OPTIONS% calculate-enrichment-analysis.py ^
    --db=%DATA_DIR%\gymnoTOA.db ^
    --app=gymnoTOA ^
    --annotations=%OUTPUT_DIR%\annotations.csv ^
    --species=all_species ^
    --method=by ^
    --msqannot=5 ^
    --msqspec=10 ^
    --goea=%OUTPUT_DIR%\goterm-enrichment-analysis-gymnotoa.csv ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% calculate-enrichment-analysis.py ^
    --db=%DATA_DIR%\gymnoTOA.db ^
    --app=TOA ^
    --annotations=%DATA_DIR%\plant-annotation.csv ^
    --species=all_species ^
    --method=by ^
    --msqannot=5 ^
    --msqspec=10 ^
    --goea=%OUTPUT_DIR%\goterm-enrichment-analysis-toa.csv ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% calculate-enrichment-analysis.py ^
    --db=%DATA_DIR%\gymnoTOA.db ^
    --app=EnTAP-runN ^
    --annotations=%DATA_DIR%\final_annotations_no_contam_lvl0.tsv ^
    --species=all_species ^
    --method=by ^
    --msqannot=5 ^
    --msqspec=10 ^
    --goea=%OUTPUT_DIR%\goterm-enrichment-analysis-entap.csv ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% calculate-enrichment-analysis.py ^
    --db=%DATA_DIR%\gymnoTOA.db ^
    --app=TRAPID ^
    --annotations=%DATA_DIR%\transcripts_go_exp1524.txt ^
    --species=all_species ^
    --method=by ^
    --msqannot=5 ^
    --msqspec=10 ^
    --goea=%OUTPUT_DIR%\goterm-enrichment-analysis-trapid.csv ^
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
