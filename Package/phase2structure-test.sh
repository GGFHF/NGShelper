
#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a phase2structure.py 
# in a Linux environment.
#
# This software has been developed by:
#
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

NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper
DATA_DIR=$TRABAJO/ProyectosVScode/NGShelper/data
OUTPUT_DIR=$TRABAJO/ProyectosVScode/NGShelper/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program phase2structure.py

/usr/bin/time \
    ./phase2structure.py \
        --phase-indir=$DATA_DIR/ULH-phase-input \
        --phase-outdir=$DATA_DIR/ULH-phase-output \
        --samples=$DATA_DIR/IDs-total.txt \
        --sp1_id=AL \
        --sp2_id=EN \
        --hyb_id=HY \
        --max_md=50 \
        --structure=$OUTPUT_DIR/phase-converted.tsv \
        --errors=%OUTPUT_DIR%/wrong-phase-filex.txt \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
