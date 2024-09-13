
#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a vcf2mach.py 
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
DATA_DIR=$NGSHELPER/data
OUTPUT_DIR=$NGSHELPER/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

INITIAL_DIR=$(pwd)
cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program vcf2mach.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS vcf2mach.py \
        --vcf=$DATA_DIR/test-SUBERINTRO-AL-J-wmd.vcf \
        --dat=$OUTPUT_DIR/test-SUBERINTRO-AL-J-wmd.dat \
        --ped=$OUTPUT_DIR/test-SUBERINTRO-AL-J-wmd.ped \
        --mdc=. \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
