#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program get-liftoff-genome-relationships.py
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

# Run the program get-liftoff-genome-relationships.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS get-liftoff-genome-relationships.py \
        --db=$DATA_DIR_DIR/comparative-genomics.db \
        --ref_sp_list=Qlobata,Qrobur,Qrubra,Qsuber \
        --tar_sp_list=Qilex,Qlobata,Qrobur,Qrubra,Qsuber \
        --map_gene_file=$OUTPUT_DIR/quercus-common-mapped-genes.csv \
        --map_codgene_file=$OUTPUT_DIR/quercus-common-mapped-coding-genes.csv \
        --map_prot_file=$OUTPUT_DIR/quercus-common-mapped-proteins.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
