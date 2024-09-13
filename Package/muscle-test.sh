#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of the program calculate-enrichment-analysis.py
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

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

SEP="#########################################"

CLUSTER_FILE=interproscan-test-Acrogymnospermae-protein-sequences-seq1000-cluster1.fasta
ALIGNMENT_FILE=interproscan-test-Acrogymnospermae-protein-sequences-seq1000-cluster1-muscle.fasta

# local
DATA_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/gymnoTOA/output
OUTPUT_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/gymnoTOA/output
# AWS
# -- DATA_DIR=/ngscloud2/gymnotoa/output-test
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test

CLUSTER_PATH=$DATA_DIR/$CLUSTER_FILE
ALIGNMENT_PATH=$DATA_DIR/$ALIGNMENT_FILE

if [ ! -d "$OUTPUT_DIR" ]; then mkdir --parents $OUTPUT_DIR; fi

#-------------------------------------------------------------------------------

function init
{

    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Script started at $FORMATTED_INIT_DATETIME."

}

#-------------------------------------------------------------------------------

function run_muscle
{

    source activate muscle

    echo "$SEP"
    echo "Aligning FASTA sequences ..."
    /usr/bin/time \
        muscle \
            -align $CLUSTER_PATH \
            -output $ALIGNMENT_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error muscle $RC; fi

    conda deactivate

}

#-------------------------------------------------------------------------------

function calculate_duration
{

    DURATION=`expr $END_DATETIME - $INIT_DATETIME`
    HH=`expr $DURATION / 3600`
    MM=`expr $DURATION % 3600 / 60`
    SS=`expr $DURATION % 60`
    FORMATTED_DURATION=`printf "%03d:%02d:%02d\n" $HH $MM $SS`

}

#-------------------------------------------------------------------------------

function end
{

    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "Script ended OK at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 0

}

#-------------------------------------------------------------------------------

function manage_error
{

    END_DATETIME=`date +%s`
    FORMATTED_END_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    calculate_duration
    echo "$SEP"
    echo "ERROR: $1 returned error $2"
    echo "Script ended WRONG at $FORMATTED_END_DATETIME with a run duration of $DURATION s ($FORMATTED_DURATION)."
    echo "$SEP"
    exit 3

}

#-------------------------------------------------------------------------------

init
run_muscle
end

#-------------------------------------------------------------------------------
