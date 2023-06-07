#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program launch-phase-processes.py
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

# Run the program launch-phase-processes.py

/usr/bin/time \
    ./launch-phase-processes.py \
        --phasedir=/home/fmm/Apps/PHASE \
        --processes=4 \
        --indir=$OUTPUT_DIR/vcf2phase \
        --outdir=$OUTPUT_DIR/phase \
        --iterations=100 \
        --thinning=1 \
        --burnin=100 \
        --otherparams=NONE \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
