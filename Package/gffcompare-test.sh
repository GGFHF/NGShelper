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
LIFTOFF_OUTPUT_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/quercusTOA/output/liftoff
GFFCOMPARE_OUTPUT_DIR=/home/fmm/Documents/Trabajo/ProyectosVScode/quercusTOA/output/gffcompare
# AWS
# -- DATA_DIR=/ngscloud2/gymnotoa/output-test
# -- LIFTOFF_OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/liftoff
# -- GFFCOMPARE_OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/liftoff

# -- REFERENCE_GFF_PATH=$DATA_DIR/GCF_001633185.2_ValleyOak3.2_genomic.gff
REFERENCE_GFF_PATH=$DATA_DIR/GCF_002906115.3_Cork_oak_2.0_genomic.gff
TARGET_GFF_PATH=$LIFTOFF_OUTPUT_DIR/target.gff

if [ ! -d "$GFFCOMPARE_OUTPUT_DIR" ]; then mkdir --parents $GFFCOMPARE_OUTPUT_DIR; fi

#-------------------------------------------------------------------------------

function init
{

    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Script started at $FORMATTED_INIT_DATETIME."

}

#-------------------------------------------------------------------------------

function run_gffcompare
{

    source activate gffcompare

    echo "$SEP"
    echo "Comparing GFF files ..."
    /usr/bin/time \
        gffcompare \
            -r $REFERENCE_GFF_PATH \
            -o $GFFCOMPARE_OUTPUT_DIR/output \
            $TARGET_GFF_PATH
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
run_gffcompare
end

#-------------------------------------------------------------------------------
