#!/bin/bash

#-------------------------------------------------------------------------------

# This script executes a test of the program load-interproscan-annotations.py
# in a Linux environment.
#
# This software has been developed by:
#
#    GI en Especies Leñosas (WooSp)
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

# Set run environment

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

# Run the program load-interproscan-annotations.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS load-interproscan-annotations.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --annotations=$DATA_DIR/Acrogymnospermae-consensus-annotations-interpro.tsv \
        --stats=$OUTPUT_DIR/Acrogymnospermae-consensus-seqs-annotation-stats.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
