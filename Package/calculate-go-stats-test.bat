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

rem This script executes a test of the program calculate-go-stats.py
rem in a Windows environment.

rem ----------------------------------------------------------------------------

rem Control parameters

if not "%*" == "" (set ERROR=1 & goto END)

rem ----------------------------------------------------------------------------

rem Set run environment

setlocal EnableDelayedExpansion

set PYTHONPATH=.
set PYTHON_OPTIONS=

set NGSHELPER_DIR=%NGSHELPER%
set DATA_DIR=%NGSHELPER_DIR%\data
set OUTPUT_DIR=%NGSHELPER_DIR%\output

set ERROR=0

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Execute the program calculate-go-stats.py

python.exe %PYTHON_OPTIONS% calculate-go-stats.py ^
    --app=Blast2GO ^
    --annotation=%DATA_DIR%\PCAN_omicsbox_table.txt ^
    --ontology=%DATA_DIR%\go.obo ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

python.exe %PYTHON_OPTIONS% calculate-go-stats.py ^
    --app=EnTAP ^
    --annotation=%DATA_DIR%\final_annotations_no_contam_lvl0.tsv ^
    --ontology=%DATA_DIR%\go.obo ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

python.exe %PYTHON_OPTIONS% calculate-go-stats.py ^
    --app=TOA ^
    --annotation=%DATA_DIR%\plant-annotation.csv ^
    --ontology=%DATA_DIR%\go.obo ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

python.exe %PYTHON_OPTIONS% calculate-go-stats.py ^
    --app=TRAPID ^
    --annotation=%DATA_DIR%\transcripts_go_exp1524.txt ^
    --ontology=%DATA_DIR%\go.obo ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

python.exe %PYTHON_OPTIONS% calculate-go-stats.py ^
    --app=Trinotate ^
    --annotation=%DATA_DIR%\trinotate_annotation_report.xls ^
    --ontology=%DATA_DIR%\go.obo ^
    --outdir=%OUTPUT_DIR% ^
    --verbose=Y ^
    --trace=N
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
