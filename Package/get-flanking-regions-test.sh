#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a get-flanking-regions.py 
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

# Run the program get-flanking-regions.py

/usr/bin/time \
    ./get-flanking-regions.py \
        --vcf=$DATA_DIR/concatenated_imputed_progenies-6000DP-scenario2.vcf \
        --genome=$DATA_DIR/GCF_002906115.1_CorkOak1.0_genomic.fna \
        --out=$OUTPUT_DIR/concatenated_imputed_progenies-6000DP-scenario2-flanking-regions.fasta \
        --nucleotides=25 \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
