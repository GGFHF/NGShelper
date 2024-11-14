#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of MMseqs2 software in a Linux environment.
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

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

# local
source $BIOCONDA/mmseqs2/util/bash-completion.sh
# AWS
# -- source /ngscloud2/apps/Miniconda3/envs/mmseqs2/util/bash-completion.sh

SEP="#########################################"

# local
MMSEQS2_DIR=$BIOCONDA/mmseqs2/bin
DATA_DIR=$GYMNOTOA/data
# AWS
# -- MMSEQS2_DIR=/ngscloud2/apps/Miniconda3/envs/mmseqs2/bin
# -- DATA_DIR=/ngscloud2/gymnotoa/data-test

FASTA_FILE=Acrogymnospermae-protein-sequences-seq1000.fasta
# -- FASTA_FILE=Acrogymnospermae-protein-sequences-seq100000.fasta
FASTA_PATH=$DATA_DIR/$FASTA_FILE

# local
OUTPUT_DIR=$GYMNOTOA/output/MMseqs2-`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
# AWS
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/MMseqs2-`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
OUTPUT_PREFIX=$OUTPUT_DIR/`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`

THREADS=4

PATH=$MMSEQS2_DIR:$PATH

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

function run_mmseqs2
{

    echo "$SEP"
    echo "Running MMseqs2 ..."
    /usr/bin/time \
        mmseqs \
            easy-cluster \
            $FASTA_PATH \
            $OUTPUT_PREFIX \
            tmp \
            --threads $THREADS \
            -c 0.8 \
            --cov-mode 1 \
            --min-seq-id 0.5
    RC=$?
    if [ $RC -ne 0 ]; then mmseqs $RC; fi

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
run_mmseqs2
end

#-------------------------------------------------------------------------------
