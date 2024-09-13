#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a debase-transcript-sequences.py 
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

# Run the program debase-transcript-sequences.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS debase-transcript-sequences.py \
        --fasta=$DATA_DIR/GS2-kinesins252seqs.fasta \
        --output=$OUTPUT_DIR/GS2-kinesins252seqs-debased.fasta \
        --fragprob=0.3  \
        --maxfragnum=3  \
        --maxshortening=5  \
        --minfraglen=50  \
        --mutprob=0.5  \
        --maxmutnum=3  \
        --indelprob=0.25  \
        --maxmutsize=10  \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
