#!/bin/bash

#-------------------------------------------------------------------------------

# This software has been developed by:
#
#    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# This script executes a test of the program filter-fasta.py in a Linux
# environment.

#-------------------------------------------------------------------------------

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set run environment

NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper
DATA_DIR=$TRABAJO/ProyectosVScode/NGShelper/data
OUTPUT_DIR=$TRABAJO/ProyectosVScode/NGShelper/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Execute the program filter-fasta.py

/usr/bin/time \
    ./filter-fasta.py \
        --fasta=$DATA_DIR/Athaliana01x-sdnt-170313-121936.scafSeq \
        --output=$OUTPUT_DIR/filtered-transcriptome.fasta \
        --minlen=200 \
        --maxlen=10000 \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
