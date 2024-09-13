#!/bin/bash

#-------------------------------------------------------------------------------

# This script performs a test ...
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

SEP="#########################################"

MAFFT='mafft'
MUSCLE='muscle'
ALIGNER=$MAFFT

ENV_LOCAL='local'
ENV_AWS='aws'
ENVIRONMENT=$ENV_AWS

if [ "$ENVIRONMENT" = "$ENV_LOCAL" ]; then

    source $BIOCONDA/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=$NGSHELPER
    MMSEQS2_DIR=$BIOCONDA/mmseqs2/bin
    DATA_DIR=$GYMNOTOA/data
    TEST_DIR=$GYMNOTOA/output

    FASTA_FILE=Acrogymnospermae-protein-sequences-seq1000.fasta
    ALLSEQS_FILE=Acrogymnospermae-protein-sequences-seq1000_all_seqs.fasta

    THREADS=4

elif [ "$ENVIRONMENT" = "$ENV_AWS" ]; then

    source /ngscloud2/apps/Miniconda3/envs/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=/ngscloud2/apps/NGShelper
    MMSEQS2_DIR=/ngscloud2/apps/Miniconda3/envs/mmseqs2/bin
    DATA_DIR=/ngscloud2/gymnotoa/data-test
    TEST_DIR=/ngscloud2/gymnotoa/output-test

    FASTA_FILE=Acrogymnospermae-protein-sequences.fasta
    ALLSEQS_FILE=Acrogymnospermae-protein-sequences_all_seqs.fasta

    THREADS=16

else
    echo 'Environment error'; exit 3
fi

OUTPUT_DIR=$TEST_DIR/MMseqs2-`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
OUTPUT_PREFIX=$OUTPUT_DIR/`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
CLUSTER_DIR=$OUTPUT_DIR/clusters
FASTA_PATH=$DATA_DIR/$FASTA_FILE
ALLSEQS_PATH=$OUTPUT_DIR/$ALLSEQS_FILE
RELATIONSHIP_FILE=`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`-relationships.csv
RELATIONSHIP_PATH=$OUTPUT_DIR/$RELATIONSHIP_FILE
IDENTITIES_FILE=`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`-identities.csv
IDENTITIES_PATH=$OUTPUT_DIR/$IDENTITIES_FILE
CONSEQS_FILE=`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`-consensus-seqs.fasta
CONSEQS_PATH=$OUTPUT_DIR/$CONSEQS_FILE

PATH=$NGSHELPER_DIR:$MMSEQS2_DIR:$PATH

if [ -d "$OUTPUT_DIR" ]; then rm -rf $OUTPUT_DIR; fi; mkdir --parents $OUTPUT_DIR 
if [ -d "$CLUSTER_DIR" ]; then rm -rf $CLUSTER_DIR; fi; mkdir --parents $CLUSTER_DIR

#-------------------------------------------------------------------------------

if [ -n "$*" ]; then echo 'This script does not have parameters'; exit 1; fi

#-------------------------------------------------------------------------------

function init
{

    INIT_DATETIME=`date +%s`
    FORMATTED_INIT_DATETIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "$SEP"
    echo "Script started at $FORMATTED_INIT_DATETIME."

}

#-------------------------------------------------------------------------------

function cluster_sequences
{

    echo "$SEP"
    echo "Clusterint sequences ..."
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
    if [ $RC -ne 0 ]; then manage_error mmseqs $RC; fi

}

#-------------------------------------------------------------------------------

function split_clusters
{

    echo "$SEP"
    echo "Spliting clusters ..."
    /usr/bin/time \
        split-mmseqs2-clusters.py \
            --allseqs=$ALLSEQS_PATH \
            --relationships=$RELATIONSHIP_PATH \
            --outdir=$CLUSTER_DIR \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error split-mmseqs2-clusters.py $RC; fi

}

#-------------------------------------------------------------------------------

function align_clusters
{

    source activate $ALIGNER

    echo "$SEP"

    CLUSTERS_FILE_LIST=$CLUSTER_DIR/clusters-files.txt
    find $CLUSTER_DIR -type f -name cluster*.fasta > $CLUSTERS_FILE_LIST
    sort --output=$CLUSTERS_FILE_LIST $CLUSTERS_FILE_LIST

    while read FILE_1; do

        echo "Aligning sequences in cluster file `basename $FILE_1` ..."

        FILE_2=`echo $FILE_1 | sed "s/.fasta/-$ALIGNER.fasta/g"`

        if [ "$ALIGNER" = "$MAFFT" ]; then

            /usr/bin/time \
                mafft \
                    --thread $THREADS \
                    --amino \
                    $FILE_1 \
                    > $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error mafft $RC; fi

        elif [ "$ALIGNER" = "$MUSCLE" ]; then

            NLIN=`grep -o '>' $FILE_1 | wc -l`
            if [ $NLIN -gt 1 ]; then
                /usr/bin/time \
                    muscle \
                        -align $FILE_1 \
                        -output $FILE_2
                RC=$?
                if [ $RC -ne 0 ]; then manage_error muscle $RC; fi
            else
                cp $FILE_1 $FILE_2
                RC=$?
                if [ $RC -ne 0 ]; then manage_error cp $RC; fi
            fi

        else
            echo 'Aligner error'; exit 3
        fi

    done < $CLUSTERS_FILE_LIST

    conda deactivate

}

#-------------------------------------------------------------------------------

function calculate_clusters_identity
{

    echo "$SEP"
    echo "Calculating identity percentage of clusters ..."
    /usr/bin/time \
        calculate-alignment-identity.py \
            --pattern=$CLUSTER_DIR/cluster*-$ALIGNER.fasta \
            --out=$IDENTITIES_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then calculate-alignment-identity.py $RC; fi

}

#-------------------------------------------------------------------------------

function calculate_consensus_seqs
{

    source activate emboss

    echo "$SEP"

    ALIGNED_CLUSTERS_FILE_LIST=$CLUSTER_DIR/aligned-clusters-files.txt
    find $CLUSTER_DIR -type f -name cluster*-$ALIGNER.fasta > $ALIGNED_CLUSTERS_FILE_LIST
    sort --output=$ALIGNED_CLUSTERS_FILE_LIST $ALIGNED_CLUSTERS_FILE_LIST

    while read FILE_1; do

        echo "Calculting consensus sequence in cluster file `basename $FILE_1` ..."

        FILE_2=`echo $FILE_1 | sed "s/-$ALIGNER.fasta/-$ALIGNER-cons.fasta/g"`

        NLIN=`grep -o '>' $FILE_1 | wc -l`
        if [ $NLIN -gt 1 ]; then
            /usr/bin/time \
                cons \
                    -sequence $FILE_1 \
                    -outseq $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error mafft $RC; fi
        else
            cp $FILE_1 $FILE_2
            RC=$?
            if [ $RC -ne 0 ]; then manage_error cp $RC; fi
        fi

    done < $ALIGNED_CLUSTERS_FILE_LIST

    conda deactivate

}

#-------------------------------------------------------------------------------

function unify_consensus_seqs
{

    echo "$SEP"
    echo 'Unifying consensus sequences ...'
    /usr/bin/time \
        unify-consensus-seqs.py \
            --pattern=$CLUSTER_DIR/cluster*-$ALIGNER-cons.fasta \
            --out=$CONSEQS_PATH \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then calculate-alignment-identity.py $RC; fi

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
cluster_sequences
split_clusters
align_clusters
calculate_clusters_identity
calculate_consensus_seqs
unify_consensus_seqs
end

#-------------------------------------------------------------------------------
