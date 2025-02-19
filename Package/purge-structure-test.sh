#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a convert-vcf.py 
# in a Linux environment.
#
# This software has been developed by:
#
#    GI en Desarrollo de Especies y Comunidades Leñosas (WooSp)
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

# Run the program purge-structure.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS purge-structure.py \
        --structure=$DATA_DIR/Scn3-real-prevalencia1.tsv \
        --format=2 \
        --operation=CHAVAL \
        --value=199 \
        --nvalue=911 \
        --out=$OUTPUT_DIR/Scn3-real-prevalencia1-purged-chaval.tsv \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS purge-structure.py \
        --structure=$DATA_DIR/Scn3-real-prevalencia1.tsv \
        --format=2 \
        --operation=DELCOL \
        --value=199 \
        --nvalue=NONE \
        --out=$OUTPUT_DIR/Scn3-real-prevalencia1-purged-delcol.tsv \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
