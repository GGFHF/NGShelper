#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a build-allele-frequency.py 
# in a Linux environment.
#
# This software has been developed by:
#
#    GI en especies leñosas (WooSp)
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

PYTHON=python3
PYTHON_OPTIONS=
PYTHONPATH=.

NGSHELPER_DIR=$NGSHELPER
DATA_DIR=$NGSHELPER/data
OUTPUT_DIR=$NGSHELPER/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program build-allele-frequency.py

# -- /usr/bin/time \
# --     $PYTHON $PYTHON_OPTIONS build-allele-frequency.py \
# --         --vcf=$DATA_DIR/concatenated_imputed_progenies-6000DP-scenario2.vcf \
# --         --samples=$DATA_DIR/IDs-total.txt \
# --         --sp1_id=AL \
# --         --sp2_id=EN \
# --         --hyb_id=HY \
# --         --outdir=$OUTPUT_DIR \
# --         --varnum=1000 \
# --         --trans=ADD100 \
# --         --verbose=Y \
# --         --trace=N \
# --         --tvi=NONE
# -- if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS build-allele-frequency.py \
        --vcf=$DATA_DIR/Selected-for-simhyb.recode.vcf \
        --samples=$DATA_DIR/keep-adults-simhyb.txt \
        --sp1_id=AL \
        --sp2_id=EN \
        --hyb_id=NONE \
        --outdir=$OUTPUT_DIR \
        --varnum=1000 \
        --trans=ATCG \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
