
#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a split-mmseqs2-clusters.py 
# in a Linux environment.
#
# This software has been developed by:
#
#    GI en especies leñosas (WooSp)
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
DATA_DIR=$GYMNOTOA/data
OUTPUT_DIR=$GYMNOTOA/output

ALLSEQS_FILE=Acrogymnospermae-protein-sequences-seq1000_all_seqs.fasta
RELATIONSHIP_FILE=relationships.csv

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program split-mmseqs2-clusters.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS split-mmseqs2-clusters.py \
        --allseqs=$DATA_DIR/$ALLSEQS_FILE \
        --relationships=$OUTPUT_DIR/$RELATIONSHIP_FILE \
        --outdir=$OUTPUT_DIR \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
