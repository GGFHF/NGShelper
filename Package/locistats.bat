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

rem This script generates statistics of haplotyope number by locus from a ypirad loci file.

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

rem Execute the program locistats.py

:LOCI2NEXUS

python.exe %PYTHON_OPTIONS% locistats.py %* %ARGV%
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
