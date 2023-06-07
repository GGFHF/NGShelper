#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a simulate-md.py 
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

# Run the program simulate-md.py

/usr/bin/time \
    ./simulate-md.py \
        --vcf=$DATA_DIR/test-SUBERINTRO-AL-samples-filtered2-sorted.vcf \
        --method=RANDOM \
        --mdp=0.20 \
        --mpiwmd=10 \
        --out=$OUTPUT_DIR/test-SUBERINTRO-AL-samples-filtered2-sorted-wmd.vcf \
        --verbose=Y \
        --trace=N \
        --tsi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
