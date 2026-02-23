@echo off

rem ----------------------------------------------------------------------------

rem This script This script build the sequence database in a Windows environment.
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
set DATA_DIR=C:\Users\FMM\quercusTOA-app-databases\quercusTOA-db
set OUTPUT_DIR=%NGSHELPER%\output

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

set INITIAL_DIR=%cd%
cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Run the program load-species-seqs.py

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=NCBI ^
    --species=Qlobata ^
    --genome=%DATA_DIR%\GCF_001633185.2_ValleyOak3.2_genomic.fna ^
    --gff=%DATA_DIR%\GCF_001633185.2_ValleyOak3.2_genomic.gff ^
    --proteins=%DATA_DIR%\GCF_001633185.2_ValleyOak3.2_protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=NCBI ^
    --species=Qrobur ^
    --genome=%DATA_DIR%\GCF_932294415.1_dhQueRobu3.1_genomic.fna ^
    --gff=%DATA_DIR%\GCF_932294415.1_dhQueRobu3.1_genomic.gff ^
    --proteins=%DATA_DIR%\GCF_932294415.1_dhQueRobu3.1_protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=NCBI ^
    --species=Qrubra ^
    --genome=%DATA_DIR%\GCA_035136125.1_Qrubra_687_v2.0_genomic.fna ^
    --gff=%DATA_DIR%\GCA_035136125.1_Qrubra_687_v2.0_genomic.gff ^
    --proteins=%DATA_DIR%\GCA_035136125.1_Qrubra_687_v2.0_protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=NCBI ^
    --species=Qsuber ^
    --genome=%DATA_DIR%\GCF_002906115.3_Cork_oak_2.0_genomic.fna ^
    --gff=%DATA_DIR%\GCF_002906115.3_Cork_oak_2.0_genomic.gff ^
    --proteins=%DATA_DIR%\GCF_002906115.3_Cork_oak_2.0_protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=CNCB-NGDC ^
    --species=Qacutissima ^
    --genome=%DATA_DIR%\GWHBGBO00000000.genome.fasta ^
    --gff=%DATA_DIR%\GWHBGBO00000000.gff ^
    --proteins=%DATA_DIR%\GWHBGBO00000000.Protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=CNCB-NGDC ^
    --species=Qdentata ^
    --genome=%DATA_DIR%\GWHBRAD00000000.genome.fasta ^
    --gff=%DATA_DIR%\GWHBRAD00000000.gff ^
    --proteins=%DATA_DIR%\GWHBRAD00000000.Protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=CNCB-NGDC ^
    --species=Qglauca ^
    --genome=%DATA_DIR%\GWHDTWU00000000.genome.fasta ^
    --gff=%DATA_DIR%\GWHDTWU00000000.gff ^
    --proteins=%DATA_DIR%\GWHDTWU00000000.Protein.faa ^
    --verbose=Y ^
    --trace=N
if %ERRORLEVEL% neq 0 (set RC=%ERRORLEVEL% & set ERROR=2 & goto END)

%PYTHON% %PYTHON_OPTIONS% load-species-seqs.py ^
    --db=%DATA_DIR%\sequences.db ^
    --server=CNCB-NGDC ^
    --species=Qvariabilis ^
    --genome=%DATA_DIR%\GWHBQTN00000000.genome.fasta ^
    --gff=%DATA_DIR%\GWHBQTN00000000.gff ^
    --proteins=%DATA_DIR%\GWHBQTN00000000.Protein.faa ^
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
