#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program a update-vcf-rlib-analysis.py 
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

# Run the program update-vcf-rlib-analysis.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS update-vcf-rlib-analysis.py \
        --mdvcffile=$DATA_DIR/test-SUBERINTRO-AL-B-wmd.vcf \
        --impvcffile=$OUTPUT_DIR/test-SUBERINTRO-AL-B-imputed-bpca.vcf \
        --analfile=$DATA_DIR/AL-B-012-bpca-imputed-rounded-t.txt \
        --verbose=Y \
        --trace=N \
        --tsi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
