@echo off

rem ----------------------------------------------------------------------------

rem This script performs a test of the program check-imputations.py
rem in a Windows environment.
rem
rem This software has been developed by:
rem
rem     GI en Especies Leñosas (WooSp)
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

set DATASET_ID=AL
set PROCESS_ID=J
set MDP=0.30
set MPIWMD=30

set ALGORITHM=SOM
set DIM=5
set SIGMA=1.0
set LR=0.5
set ITER=1000
set MR2=0.1
set SNPS=5
set GIM=MF
set HIGH_LD_SITES=%ALGORITHM%
set NN=%ALGORITHM%
set MAX_DIST=%ALGORITHM%

set EXPERIMENT_ID=SUBERINTRO-%DATASET_ID%-%PROCESS_ID%
set ROOT_NAME=test-%EXPERIMENT_ID%

set DB_PATH=%DATA_DIR%\%ROOT_NAME%.db
set VCF_WMD_PATH=%DATA_DIR%\%ROOT_NAME%-3-wmd.vcf
set IMPUTED_VCF_PATH=%DATA_DIR%\%ROOT_NAME%-imputed-%DIM%x%DIM%-%SIGMA%-%MR2%-%SNPS%-%GIM%.vcf
set MAP_PATH=%OUTPUT_DIR%\%ROOT_NAME%-imputed-%DIM%x%DIM%-%SIGMA%-%MR2%-%SNPS%-%GIM%-map.csv
set SUMMARY_PATH=%OUTPUT_DIR%\%ROOT_NAME%-summary.csv
set CM_PATH=%OUTPUT_DIR%\%ROOT_NAME%-imputed-%DIM%x%DIM%-%SIGMA%-%MR2%-%SNPS%-%GIM%-cm.csv

rem -- set ALGORITHM=TASSEL
rem -- set DIM=%ALGORITHM%
rem -- set SIGMA=%ALGORITHM%
rem -- set LR=%ALGORITHM%
rem -- set ITER=%ALGORITHM%
rem -- set MR2=%ALGORITHM%
rem -- set SNPS=%ALGORITHM%
rem -- set GIM=%ALGORITHM%
rem -- set HIGH_LD_SITES=15
rem -- set NN=5
rem -- set MAX_DIST=10000000

rem -- set EXPERIMENT_ID=SUBERINTRO-%DATASET_ID%-%PROCESS_ID%
rem -- set ROOT_NAME=test-%EXPERIMENT_ID%

rem -- set DB_PATH=%DATA_DIR%\%ROOT_NAME%.db
rem -- set VCF_WMD_PATH=%DATA_DIR%\%ROOT_NAME%-wmd-sorted.vcf
rem -- set IMPUTED_VCF_PATH=%DATA_DIR%\%ROOT_NAME%-wmd-sorted-TASSEL-S%HIGH_LD_SITES%-N%NN%-D%MAX_DIST%.vcf
rem -- set MAP_PATH=%OUTPUT_DIR%\%ROOT_NAME%-wmd-sorted-TASSEL-S%HIGH_LD_SITES%-N%NN%-D%MAX_DIST%-map.csv
rem -- set SUMMARY_PATH=%OUTPUT_DIR%\%ROOT_NAME%-summary-TASSEL.csv
rem -- set CM_PATH=%OUTPUT_DIR%\%ROOT_NAME%-wmd-sorted-TASSEL-S%HIGH_LD_SITES%-N%NN%-D%MAX_DIST%-cm.csv

rem -- set ALGORITHM=naive
rem -- set DIM=%ALGORITHM%
rem -- set SIGMA=%ALGORITHM%
rem -- set LR=%ALGORITHM%
rem -- set ITER=%ALGORITHM%
rem -- set MR2=%ALGORITHM%
rem -- set SNPS=%ALGORITHM%
rem -- set GIM=%ALGORITHM%F
rem -- set HIGH_LD_SITES=%ALGORITHM%
rem -- set NN=%ALGORITHM%
rem -- set MAX_DIST=%ALGORITHM%

rem -- set EXPERIMENT_ID=%DATASET_ID%-%PROCESS_ID%
rem -- set ROOT_NAME=test-%EXPERIMENT_ID%

rem -- set DB_PATH=%DATA_DIR%\%ROOT_NAME%.db
rem -- set VCF_WMD_PATH=%DATA_DIR%\%ROOT_NAME%-3-wmd.vcf
rem -- set IMPUTED_VCF_PATH=%DATA_DIR%\%ROOT_NAME%-imputed-%ALGORITHM%.vcf
rem -- set MAP_PATH=%OUTPUT_DIR%\%ROOT_NAME%-imputed-%ALGORITHM%-map.csv
rem -- set SUMMARY_PATH=%OUTPUT_DIR%\%ROOT_NAME%-summary-%ALGORITHM%.csv
rem -- set CM_PATH=%OUTPUT_DIR%\%ROOT_NAME%-imputed-%ALGORITHM%-cm.csv

set EXPDATA=%ALGORITHM%;%EXPERIMENT_ID%;%DATASET_ID%;RANDOM;%MDP%;%MPIWMD%;%DIM%x%DIM%;%SIGMA%;%LR%;%ITER%;%MR2%;%SNPS%;%GIM%;%HIGH_LD_SITES%;%NN%;%MAX_DIST%

if not exist %OUTPUT_DIR% (mkdir %OUTPUT_DIR%)

set INITIAL_DIR=%cd%
cd %NGSHELPER_DIR%

rem ----------------------------------------------------------------------------

rem Run the program check-imputations.py

echo file_name;algorithm;experiment_id;dataset_id;method;mdp;mpiwmd;dim;sigma;lr;iter;mr2;snps;gim;high_ld_sites;nn;max_dist;ok_genotypes_counter;ko_genotypes_counter;genotypes_withmd_counter;ok_imputed_genotypes_counter;ko_imputed_genotypes_counter;average_accuracy;error_rate;micro_precision;micro_recall;micro_fscore;macro_precision;macro_recall;macro_fscore;macro_precision_zde;macro_recall_zde > %SUMMARY_PATH%

%PYTHON% %PYTHON_OPTIONS% check-imputations.py ^
    --db=%DB_PATH% ^
    --chvcffile=%IMPUTED_VCF_PATH% ^
    --mdvcffile=%VCF_WMD_PATH% ^
    --mapfile=%MAP_PATH% ^
    --summfile=%SUMMARY_PATH% ^
    --cmfile=%CM_PATH% ^
    --expdata=%EXPDATA% ^
    --verbose=Y ^
    --trace=N ^
    --tsi=NONE
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
