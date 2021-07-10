
#!/bin/bash

#-------------------------------------------------------------------------------

# This software has been developed by:
#
#    GI Sistemas Naturales e Historia Forestal (formerly known as GI Genetica, Fisiologia e Historia Forestal)
#    Dpto. Sistemas y Recursos Naturales
#    ETSI Montes, Forestal y del Medio Natural
#    Universidad Politecnica de Madrid
#    https://github.com/ggfhf/
#
# Licence: GNU General Public Licence Version 3.

#-------------------------------------------------------------------------------

# This script executes a test of the program collapse-vcf-indels.py 
# in a Linux environment.

#-------------------------------------------------------------------------------

# Control parameters

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# Set run environment

NGSHELPER_DIR=$TRABAJO/ProyectosVScode/NGShelper
DATA_DIR=$TRABAJO/ProyectosVScode/NGShelper/data
OUTPUT_DIR=$TRABAJO/ProyectosVScode/NGShelper/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Execute the program collapse-vcf-indels.py

/usr/bin/time \
    ./collapse-vcf-indels.py \
        --vcf=$DATA_DIR/NW_019805656.1.vcf \
        --samples=$DATA_DIR/IDs-total.txt \
        --imd_id=99 \
        --sp1_id=AL \
        --sp2_id=EN \
        --hyb_id=HY \
        --out=$OUTPUT_DIR/NW_019805656.1-collapsed.vcf \
        --stats=$OUTPUT_DIR/NW_019805656.1-stats.txt \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
