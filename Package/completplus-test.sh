#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of Complet-Plus software in a Linux environment.
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

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

SEP="#########################################"

# local
COMPLETPLUS_DIR=$APPS/Complet-Plus/complet-plus-scripts
DATA_DIR=$GYMNOTOA/output/MMseqs2-Acrogymnospermae-protein-sequences-seq1000
OUTPUT_DIR=$GYMNOTOA/output/MMseqs2-Acrogymnospermae-protein-sequences-seq1000
# AWS
# -- COMPLETPLUS_DIR=/ngscloud2/apps/Complet-Plus/complet-plus-scripts
# -- DATA_DIR=/ngscloud2/output-test/MMseqs2-Acrogymnospermae-protein-sequences-seq1000
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/MMseqs2-Acrogymnospermae-protein-sequences-seq1000

CLUSTER_RESULT_FILE=Acrogymnospermae-protein-sequences-seq1000_cluster.tsv
# -- CLUSTER_RESULT_PATH=$DATA_DIR/$CLUSTER_RESULT_FILE
SEQUENCE_RESULT_FILE=Acrogymnospermae-protein-sequences-seq1000_all_seqs.fasta
# -- SEQUENCE_RESULT_PATH=$DATA_DIR/$SEQUENCE_RESULT_FILE
COMPLETPLUS_FILE=Acrogymnospermae-protein-sequences-seq1000_completeplus.tsv
# -- COMPLETPLUS_PATH=$OUTPUT_DIR/$COMPLETPLUS_FILE

PATH=$COMPLETPLUS_DIR:$PATH

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

function run_completplus
{

    echo "$SEP"
    echo "Running Complet-Plus ..."
    /usr/bin/time \
        completplus.sh \
           $CLUSTER_RESULT_FILE \
           $SEQUENCE_RESULT_FILE \
           $COMPLETPLUS_FILE
    RC=$?
    if [ $RC -ne 0 ]; then manage_error completplus.sh $RC; fi

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
run_completplus
end

#-------------------------------------------------------------------------------
