#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program generate-id-files.py
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

# Run the program generate-id-files.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS generate-id-files.py \
        --sp1_id=AL \
        --sp1_totinds=98 \
        --sp1_selinds=10 \
        --sp2_id=NONE \
        --sp2_totinds=0 \
        --sp2_selinds=0 \
        --hyb_id=NONE \
        --hyb_totinds=0 \
        --hyv_selinds=0 \
        --outfile1=$OUTPUT_DIR/individual-id-file-1.txt \
        --outfile2=$OUTPUT_DIR/individual-id-file-2.txt \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
