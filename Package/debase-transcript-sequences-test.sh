#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a debase-transcript-sequences.py 
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

# Run the program debase-transcript-sequences.py

/usr/bin/time \
    ./debase-transcript-sequences.py \
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

exit 0

#-------------------------------------------------------------------------------
