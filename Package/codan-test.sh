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

# local
MODEL_DIR=$BIOCONDA/codan/models
TRANSCRIPTOME_FILE=06-Pinaster-100unigenes.fasta
TRANSCRIPTOME_PATH=$GYMNOTOA/data/$TRANSCRIPTOME_FILE
OUTPUT_DIR=$GYMNOTOA/output/codan-`echo "$(n=${TRANSCRIPTOME_FILE##*/}; echo ${n%.*})"`
# AWS
# -- MODEL_DIR=/ngscloud2/apps/codan-models
# -- TRANSCRIPTOME_FILE=06-Pinaster-100unigenes.fasta
# -- TRANSCRIPTOME_PATH=/ngscloud2/gymnotoa/data-test/$TRANSCRIPTOME_FILE
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/codan-`echo "$(n=${TRANSCRIPTOME_FILE##*/}; echo ${n%.*})"`

MODEL_FULL=$MODEL_DIR/PLANTS_full
MODEL_PARTIAL=$MODEL_DIR/PLANTS_partial
CURRENT_MODEL=$MODEL_PARTIAL

NCPUS=4

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

function run_codan
{

    source activate codan

    echo "$SEP"
    echo "Predicting ORFs and getting peptide sequences ..."
    /usr/bin/time \
        codan.py \
            --cpu $NCPUS \
            --model=$CURRENT_MODEL \
            --transcripts=$TRANSCRIPTOME_PATH \
            --output=$OUTPUT_DIR
    RC=$?
    if [ $RC -ne 0 ]; then manage_error codan.py $RC; fi
    if [[ "$CURRENT_MODEL" == "$MODEL_PARTIAL" ]]; then
        /usr/bin/time \
            TranslatePartial.py \
                $OUTPUT_DIR/ORF_sequences.fasta \
                $OUTPUT_DIR/PEP_sequences.fa
        RC=$?
        if [ $RC -ne 0 ]; then manage_error TranslatePartial.py $RC; fi
    fi

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
run_codan
end

#-------------------------------------------------------------------------------
