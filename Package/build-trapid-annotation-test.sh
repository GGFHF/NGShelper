#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a build-trapid-annotation.py 
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

# Run the program build-trapid-annotation.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS build-trapid-annotation.py \
        --go=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --gf=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --ko=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --annotation==$OUTPUT_DIR/TRAPID-Fsyl-annotations.csv \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
