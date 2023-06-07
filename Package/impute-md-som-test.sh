#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a impute-md-som.py 
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

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program impute-md-som.py

/usr/bin/time \
    ./impute-md-som.py \
        --threads=4 \
        --db=$DATA_DIR/ddRADseqTools2.db \
        --vcf=$DATA_DIR/variants-nonko.vcf \
        --out=$OUTPUT_DIR/variants-nonko-imputed.vcf \
        --xdim=5 \
        --ydim=5 \
        --sigma=1.0 \
        --ilrate=0.5 \
        --iter=1000 \
        --mr2=0.001 \
        --estimator=ru \
        --snps=5 \
        --gim=MF \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
