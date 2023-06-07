#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program check-imputations.py 
# in a Linux environment.
#
# This software has been developed by:
#
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set environment

NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper
DATA_DIR=$TRABAJO/ProyectosVScode/NGShelper/data
OUTPUT_DIR=$TRABAJO/ProyectosVScode/NGShelper/output

DATASET_ID=AL
PROCESS_ID=J
MDP=0.30
MPIWMD=30

ALGORITHM=SOM
DIM=5
SIGMA=1.0
LR=0.5
ITER=1000
MR2=0.1
SNPS=5
GIM=MF
HIGH_LD_SITES=$ALGORITHM
NN=$ALGORITHM
MAX_DIST=$ALGORITHM

EXPERIMENT_ID=SUBERINTRO-$DATASET_ID-$PROCESS_ID
ROOT_NAME=test-$EXPERIMENT_ID

DB_PATH=$DATA_DIR/$ROOT_NAME.db
VCF_WMD_PATH=$DATA_DIR/$ROOT_NAME-3-wmd.vcf
IMPUTED_VCF_PATH=$DATA_DIR/$ROOT_NAME'-imputed-'$DIM'x'$DIM'-'$SIGMA'-'$MR2'-'$SNPS'-'$GIM'.vcf'
MAP_PATH=$OUTPUT_DIR/$ROOT_NAME'-imputed-'$DIM'x'$DIM'-'$SIGMA'-'$MR2'-'$SNPS'-'$GIM'-map.csv'
SUMMARY_PATH=$OUTPUT_DIR/$ROOT_NAME-summary.csv
CM_PATH=$OUTPUT_DIR/$ROOT_NAME'-imputed-'$DIM'x'$DIM'-'$SIGMA'-'$MR2'-'$SNPS'-'$GIM'-cm.csv'

# -- ALGORITHM=TASSEL
# -- DIM=$ALGORITHM
# -- SIGMA=$ALGORITHM
# -- LR=$ALGORITHM
# -- ITER=$ALGORITHM
# -- MR2=$ALGORITHM
# -- SNPS=$ALGORITHM
# -- GIM=$ALGORITHM
# -- HIGH_LD_SITES=15
# -- NN=5
# -- MAX_DIST=10000000

# -- EXPERIMENT_ID=SUBERINTRO-$DATASET_ID-$PROCESS_ID
# -- ROOT_NAME=test-$EXPERIMENT_ID

# -- DB_PATH=$DATA_DIR/$ROOT_NAME.db
# -- VCF_WMD_PATH=$DATA_DIR/$ROOT_NAME-wmd-sorted.vcf
# -- IMPUTED_VCF_PATH=$DATA_DIR/$ROOT_NAME'-wmd-sorted-TASSEL-S'$HIGH_LD_SITES'-N'$NN'-D'$MAX_DIST'.vcf'
# -- MAP_PATH=$OUTPUT_DIR/$ROOT_NAME'-wmd-sorted-TASSEL-S'$HIGH_LD_SITES'-S'$NN'-'S$MAX_DIST'-map.csv'
# -- SUMMARY_PATH=$OUTPUT_DIR/$ROOT_NAME-summary-TASSEL.csv
# -- CM_PATH=$OUTPUT_DIR/$ROOT_NAME'-wmd-sorted-TASSEL-S'$HIGH_LD_SITES'-N'$NN'-D'$MAX_DIST'-cm.csv'

# -- ALGORITHM=naive
# -- DIM=$ALGORITHM
# -- SIGMA=$ALGORITHM
# -- LR=$ALGORITHM
# -- ITER=$ALGORITHM
# -- MR2=$ALGORITHM
# -- SNPS=$ALGORITHM
# -- GIM=$ALGORITHM
# -- HIGH_LD_SITES=$ALGORITHM
# -- NN=$ALGORITHM
# -- MAX_DIST=$ALGORITHM

# -- EXPERIMENT_ID=$DATASET_ID-$PROCESS_ID
# -- ROOT_NAME=test-$EXPERIMENT_ID

# -- DB_PATH=$DATA_DIR/$ROOT_NAME.db
# -- VCF_WMD_PATH=$DATA_DIR/$ROOT_NAME-3-wmd.vcf
# -- IMPUTED_VCF_PATH=$DATA_DIR/$ROOT_NAME'-imputed-'$ALGORITHM'.vcf'
# -- MAP_PATH=$OUTPUT_DIR/$ROOT_NAME'-imputed-'$ALGORITHM'-map.csv'
# -- SUMMARY_PATH=$OUTPUT_DIR/$ROOT_NAME-summary-$ALGORITHM.csv
# -- CM_PATH=$OUTPUT_DIR/$ROOT_NAME'-imputed-'$ALGORITHM'-cm.csv'

EXPDATA=$ALGORITHM';'$EXPERIMENT_ID';'$DATASET_ID';RANDOM;'$MDP';'$MPIWMD';'$DIM'x'$DIM';'$SIGMA';'$LR';'$ITER';'$MR2';'$SNPS';'$GIM';'$HIGH_LD_SITES';'$NN';'$MAX_DIST

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program check-imputations.py

echo 'file_name;algorithm;experiment_id;dataset_id;method;mdp;mpiwmd;dim;sigma;lr;iter;mr2;snps;gim;high_ld_sites;nn;max_dist;ok_genotypes_counter;ko_genotypes_counter;genotypes_withmd_counter;ok_imputed_genotypes_counter;ko_imputed_genotypes_counter;average_accuracy;error_rate;micro_precision;micro_recall;micro_fscore;macro_precision;macro_recall;macro_fscore;macro_precision_zde;macro_recall_zde' > $SUMMARY_PATH

/usr/bin/time \
    ./check-imputations.py \
        --db=$DB_PATH \
        --chvcffile=$IMPUTED_VCF_PATH \
        --mdvcffile=$VCF_WMD_PATH \
        --mapfile=$MAP_PATH \
        --summfile=$SUMMARY_PATH \
        --cmfile=$CM_PATH \
        --expdata=$EXPDATA \
        --verbose=Y \
        --trace=N \
        --tsi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
