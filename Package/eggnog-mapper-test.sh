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

DATA_DIR=$TRABAJO/ProyectosVScode/gymnoTOA/data
OUTPUT_DIR=$TRABAJO/ProyectosVScode/gymnoTOA/output

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

function run_eggnog_mapper_diamond
{

    echo "$SEP"
    echo "Running eggNOG-mapper (diamond) ..."
    source activate eggnog-mapper
    /usr/bin/time \
        emapper.py \
           --cpu 4 \
           -i $DATA_DIR/GOs-FASTAs-03-PEP_sequences.fa \
           --itype proteins \
           -m diamond \
           --dmnd_algo auto \
           --sensmode sensitive \
           --dmnd_iterate yes \
           --evalue 0.001 \
           --outfmt "6 delim=; qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
           --output_dir $OUTPUT_DIR \
           --output GOs-FASTAs-03-PEP_sequences-diamond
    RC=$?
    if [ $RC -ne 0 ]; then manage_error emapper.py $RC; fi
    conda deactivate

}

#-------------------------------------------------------------------------------

function run_eggnog_mapper_mmseqs2
{

    echo "$SEP"
    echo "Running eggNOG-mapper (mmseqs2) ..."
    source activate eggnog-mapper
    /usr/bin/time \
        emapper.py \
           --cpu 4 \
           -i $DATA_DIR/GOs-FASTAs-03-PEP_sequences.fa \
           --itype proteins \
           -m mmseqs \
           --start_sens 3 \
           --sens_steps 3 \
           --final_sens 7 \
           --evalue 0.001 \
           --outfmt "6 delim=; qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore" \
           --output_dir $OUTPUT_DIR \
           --output GOs-FASTAs-03-PEP_sequences-mmseqs2
    RC=$?
    if [ $RC -ne 0 ]; then manage_error emapper.py $RC; fi
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
run_eggnog_mapper_diamond
run_eggnog_mapper_mmseqs2
end

#-------------------------------------------------------------------------------
