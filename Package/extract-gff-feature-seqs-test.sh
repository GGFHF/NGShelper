#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program extract-gff-feature-seqs.py
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

# Run the program extract-gff-feature-seqs.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS extract-gff-feature-seqs.py \
        --genome=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.fna \
        --gff=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.gff \
        --gene-file=$OUTPUT_DIR/Qlobata-gff-gene.fasta \
        --cds-file=$OUTPUT_DIR/Qlobata-gff-cds.fasta \
        --concds-file=$OUTPUT_DIR/Qlobata-gff-concatenated-cds.fasta \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
