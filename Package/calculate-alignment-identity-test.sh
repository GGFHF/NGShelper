
#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a calculate-alignment-identity.py 
# in a Linux environment.
#
# This software has been developed by:
#
#    GI en Especies Leñosas (WooSp)
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

# Run the program calculate-alignment-identity.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS calculate-alignment-identity.py \
        --indir=$DATA_DIR \
        --pattern=interproscan-test-Acrogymnospermae-protein-sequences-seq1000-cluster.*-mafft.fasta \
        --out=$OUTPUT_DIR/interproscan-test-Acrogymnospermae-protein-sequences-seq1000-mafft-idenpercent.txt \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
