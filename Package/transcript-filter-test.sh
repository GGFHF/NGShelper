#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program transcript-filter.py
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

# Run the program transcript-filter.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS transcript-filter.py \
        --assembler=sdnt \
        --transcriptome=$DATA_DIR/Athaliana01x-sdnt-170313-121936.scafSeq \
        --score=$DATA_DIR/rsemeval-170327-164507.genes.results \
        --output=$OUTPUT_DIR/filtered-transcriptome.fasta \
        --minlen=200 \
        --maxlen=10000 \
        --minFPKM=1.0 \
        --minTPM=1.0 \
        --verbose=Y \
		--trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
