#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program get-liftoff-gff-data.py
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

REFERENCE_SPECIES=Qlobata
TARGET_SPECIES=Qsuber
NGSHELPER_DIR=$NGSHELPER
DATA_DIR=/home/fmm/Documents/ProyectosVScode/quercusTOA/output/Quercus-comparative
OUTPUT_DIR=/home/fmm/Documents/ProyectosVScode/quercusTOA/output/Quercus-comparative

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program get-liftoff-gff-data.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS get-liftoff-gff-data.py \
        --rspecies=$REFERENCE_SPECIES \
        --tspecies=$TARGET_SPECIES \
        --gff=$DATA_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-liftoff-target.gff \
        --gene-file=$OUTPUT_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-gff_gene_data.csv \
        --cds-file=$OUTPUT_DIR/$REFERENCE_SPECIES-$TARGET_SPECIES-gff_cds_data.csv \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
