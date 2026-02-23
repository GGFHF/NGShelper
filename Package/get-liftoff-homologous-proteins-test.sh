#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program get-liftoff-homologous-proteins.py
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

# Run the program get-liftoff-homologous-proteins.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS get-liftoff-homologous-proteins.py \
        --db=$DATA_DIR_DIR/comparative-genomics.db \
        --ref_sp=Qlobata \
        --tar_sp=Qrobur \
        --map_prot_file=$DATA_DIR/Quercus-common-mapped-proteins.csv \
        --threshold=0 ^
        --verbose=Y \
        --trace=Y \
        --tpi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
