
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

# This script executes a test of the program  a build-trapid-annotation.py 
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

# Execute the program build-trapid-annotation.py

/usr/bin/time \
    ./build-trapid-annotation.py \
        --go=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --gf=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --ko=/home/fmm/Documents/DIFA-TD/TOA/results-03/TRAPID-Fsyl/transcripts_go_exp1685.txt \
        --annotation==$OUTPUT_DIR/TRAPID-Fsyl-annotations.csv \
        --verbose=Y \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

exit 0

#-------------------------------------------------------------------------------
