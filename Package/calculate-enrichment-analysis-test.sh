#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program calculate-enrichment-analysis.py
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

# Execute the program calculate-enrichment-analysis.py

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS calculate-enrichment-analysis.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --app=gymnoTOA \
        --annotations=$DATA_DIR/functional-annotations-besthit.csv \
        --species=all_species \
        --method=by \
        --msqannot=5 \
        --msqspec=10 \
        --goea=$OUTPUT_DIR/goterm-enrichment-analysis-gymnotoa.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS calculate-enrichment-analysis.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --app=TOA \
        --annotations=$DATA_DIR/plant-annotation.csv \
        --species=all_species \
        --method=by \
        --msqannot=5 \
        --msqspec=10 \
        --goea=$OUTPUT_DIR/goterm-enrichment-analysis-toa.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS calculate-enrichment-analysis.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --app=EnTAP-runN \
        --annotations=$DATA_DIR/final_annotations_no_contam_lvl0.tsv \
        --species=all_species \
        --method=by \
        --msqannot=5 \
        --msqspec=10 \
        --goea=$OUTPUT_DIR/goterm-enrichment-analysis-entap.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

/usr/bin/time \
    $PYTHON $PYTHON_OPTIONS calculate-enrichment-analysis.py \
        --db=$DATA_DIR/gymnoTOA.db \
        --app=TRAPID \
        --annotations=$DATA_DIR/transcripts_go_exp1524.txt \
        --species=all_species \
        --method=by \
        --msqannot=5 \
        --msqspec=10 \
        --goea=$OUTPUT_DIR/goterm-enrichment-analysis-trapid.csv \
        --verbose=Y  \
        --trace=N
if [ $? -ne 0 ]; then echo 'Script ended with errors.'; exit 1; fi

#-------------------------------------------------------------------------------

# End

cd $INITIAL_DIR

exit 0

#-------------------------------------------------------------------------------
