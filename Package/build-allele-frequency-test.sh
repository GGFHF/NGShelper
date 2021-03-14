
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

# This script executes a test of the program  a build-allele-frequency.py 
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

# Execute the program build-allele-frequency.py

# -- /usr/bin/time \
# --     ./build-allele-frequency.py \
# --         --vcf=$DATA_DIR/concatenated_imputed_progenies-6000DP-scenario2.vcf \
# --         --samples=$DATA_DIR/IDs-total.txt \
# --         --sp1_id=AL \
# --         --sp2_id=EN \
# --         --hyb_id=HY \
# --         --outdir=$OUTPUT_DIR \
# --         --varnum=1000 \
# --         --trans=ADD100 \
# --         --verbose=Y \
# --         --trace=N \
# --         --tvi=NONE
# -- if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    ./build-allele-frequency.py \
        --vcf=$DATA_DIR/Selected-for-simhyb.recode.vcf \
        --samples=$DATA_DIR/keep-adults-simhyb.txt \
        --sp1_id=AL \
        --sp2_id=EN \
        --hyb_id=NONE \
        --outdir=$OUTPUT_DIR \
        --varnum=1000 \
        --trans=ATCG \
        --verbose=Y \
        --trace=N \
        --tvi=NONE
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
