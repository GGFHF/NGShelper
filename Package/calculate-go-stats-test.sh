#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program  a calculate-go-stats.py 
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

PYTHONPATH=.

NGSHELPER_DIR=$NGSHELPER
DATA_DIR=$NGSHELPER_DIR/data
OUTPUT_DIR=$NGSHELPER_DIR/output

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

cd $NGSHELPER_DIR

#-------------------------------------------------------------------------------

# Run the program calculate-go-stats.py

/usr/bin/time \
    ./calculate-go-stats.py \
        --app=Blast2GO \
        --annotation=$DATA_DIR/PCAN_omicsbox_table.txt \
        --ontology=$DATA_DIR/go.obo \
        --outdir=$OUTPUT_DIR \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    ./calculate-go-stats.py \
        --app=EnTAP \
        --annotation=$DATA_DIR/final_annotations_no_contam_lvl0.tsv \
        --ontology=$DATA_DIR/go.obo \
        --outdir=$OUTPUT_DIR \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    ./calculate-go-stats.py \
        --app=TOA \
        --annotation=$DATA_DIR/plant-annotation.csv \
        --ontology=$DATA_DIR/go.obo \
        --outdir=$OUTPUT_DIR \
        --toasel=LEVWD \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    ./calculate-go-stats.py \
        --app=TRAPID \
        --annotation=$DATA_DIR/transcripts_go_exp1524.txt \
        --ontology=$DATA_DIR/go.obo \
        --outdir=$OUTPUT_DIR \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    ./calculate-go-stats.py \
        --app=Trinotate \
        --annotation=$DATA_DIR/trinotate_annotation_report.xls \
        --ontology=$DATA_DIR/go.obo \
        --outdir=$OUTPUT_DIR \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

echo
echo '**************************************************'
exit 0

#-------------------------------------------------------------------------------
