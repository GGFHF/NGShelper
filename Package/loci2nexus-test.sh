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

# This script executes a test of the program loci2nexus.py in a Linux 
# environment.

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

# Execute the program loci2nexus.py

/usr/bin/time \
    ./loci2nexus.py \
        --loci_id_file=$DATA_DIR/Lapa_GC_Less-CLUST85_SNP40_MIN80-loci-list.txt \
        --complete_loci_file=$DATA_DIR/Lapa_GC_Less-CLUST85_SNP40_MIN80.loci \
        --selected_loci_file=$OUTPUT_DIR/Lapa_GC_Less-CLUST85_SNP40_MIN80-selected.loci \
        --nexus_file=$OUTPUT_DIR/Lapa_GC_Less-CLUST85_SNP40_MIN80-selected.nex \
        --verbose=Y \
		--trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
