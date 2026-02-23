#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program remove-gff-redundancies.py
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
DATA_DIR=$NGSHELPER/data
OUTPUT_DIR=$NGSHELPER/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program remove-gff-redundancies.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS remove-gff-redundancies.py \
        --db=$DATA_DIR/Qlobata-concatenated-cds-clusters.db \
        --input-gff=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.gff \
        --output-gff=$OUTPUT_DIR/Qlobata-without-redundancies.gff \
        --redundancies=$OUTPUT_DIR/Qlobata-redundancies.txt \
        --verbose=Y \
        --trace=N \
        --tgi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS remove-gff-redundancies.py \
        --db=$DATA_DIR/Qvariabilis-concatenated-cds-clusters.db \
        --input-gff=$DATA_DIR/GWHBQTN00000000.gff \
        --output-gff=$OUTPUT_DIR/Qvariabilis-without-redundancies.gff \
        --redundancies=$OUTPUT_DIR/Qvariabilis-redundancies.txt \
        --verbose=Y \
        --trace=N \
        --tgi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
