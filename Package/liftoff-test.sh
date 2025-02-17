#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test of Liftoff software in a Linux environment.
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

SEP="#########################################"

# local
DATA_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/quercusTOA/data
OUTPUT_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/quercusTOA/output/liftoff
# AWS
# -- DATA_DIR=/ngscloud2/gymnotoa/output-test
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/liftoff

REFERENCE_GENOME_PATH=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.fna
REFERENCE_GFF_PATH=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.gff
TARGET_GENOME_PATH=$DATA_DIR/GCF_002906115.3_Cork_oak_2.0_genomic.fna
# -- TARGET_GENOME_PATH=$DATA_DIR/Qusu_TSA.fasta
TARGET_GFF_PATH=$OUTPUT_DIR/target.gff
UNMAPPED_FEATURES_PATH=$OUTPUT_DIR/unmapped.txt
INTERMEDIATE_FILES_PATH=$OUTPUT_DIR/temp-liftoff

THREADS=4

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

function run_liftoff
{

    source activate liftoff

    echo "$SEP"
    echo "Annotating the target genome ..."
    /usr/bin/time \
        liftoff \
            -p $THREADS \
            -g $REFERENCE_GFF_PATH \
            -o $TARGET_GFF_PATH \
            -copies \
            -u $UNMAPPED_FEATURES_PATH \
            -dir $INTERMEDIATE_FILES_PATH \
            $TARGET_GENOME_PATH \
            $REFERENCE_GENOME_PATH
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mafft $RC; fi

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
run_liftoff
end

#-------------------------------------------------------------------------------
