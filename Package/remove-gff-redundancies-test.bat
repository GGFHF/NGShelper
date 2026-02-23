@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program remove-gff-redundancies.py
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

rem Run the program remove-gff-redundancies.py

%PYTHON% %PYTHON_OPTIONS% remove-gff-redundancies.py ^
    --db=%DATA_DIR%\Qlobata-concatenated-cds-clusters.db ^
    --input-gff=%DATA_DIR%\GCF_001633185.2_ValleyOak3.2_genomic.gff ^
    --output-gff=%OUTPUT_DIR%\Qlobata-without-redundancies.gff ^
    --redundancies=%OUTPUT_DIR%\Qlobata-redundancies.txt ^
    --verbose=Y ^
    --trace=Y ^
    --tgi=gene-LOC115991968,gene-LOC115965322,gene-LOC115966021,gene-LOC115973679,gene-LOC115973650
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% remove-gff-redundancies.py ^
    --db=%DATA_DIR%\Qvariabilis-concatenated-cds-clusters.db ^
    --input-gff=%DATA_DIR%\GWHBQTN00000000.gff ^
    --output-gff=%OUTPUT_DIR%\Qvariabilis-without-redundancies.gff ^
    --redundancies=%OUTPUT_DIR%\Qvariabilis-redundancies.txt ^
    --verbose=Y ^
    --trace=Y ^
    --tgi=Quvar01aG0000700,Quvar01aG0002700,Quvar01aG0003900,Quvar01aG0004500,Quvar01aG0004600,Quvar09aG0212900
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
