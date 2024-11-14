#!/bin/bash

#-------------------------------------------------------------------------------

# This script yields consensus sequences in a Linux environment.
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

SEP="#########################################"

MAFFT='mafft'
MUSCLE='muscle'
ALIGNER=$MAFFT

S=(4.0)                             # s (sensitivity)
C=(0.8 0.9 1.0)                     # c (list matches above this fraction of aligned -covered- residue)
CM=0                                # cov-mode: 0 (coverage of query and target)
MSI=(0.850 0.900 0.950 0.975 1.000) # min-seq-id
ST=2                                # similarity-type: 2 (sequence identity)
TYPE=1                              # dbtype: 1 (amino acid)

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
    RELATIONSHIPS_FILE=Acrogymnospermae-protein-sequences-seq1000-relationships.csv
    IDENTITIES_FILE=Acrogymnospermae-protein-sequences-seq1000-identities.csv
    CONSEQS_FILE=Acrogymnospermae-protein-sequences-seq1000-consensus.fasta

    THREADS=4

elif [ "$ENVIRONMENT" = "$ENV_AWS" ]; then

    source /ngscloud2/apps/Miniconda3/envs/mmseqs2/util/bash-completion.sh

    NGSHELPER_DIR=/ngscloud2/apps/NGShelper
    MMSEQS2_DIR=/ngscloud2/apps/Miniconda3/envs/mmseqs2/bin
    DATA_DIR=/ngscloud2/gymnotoa/test-data
    TEST_DIR=/ngscloud2/gymnotoa/test-results

    FASTA_FILE=Acrogymnospermae-protein-sequences.fasta
    ALLSEQS_FILE=Acrogymnospermae-protein-sequences_all_seqs.fasta
    RELATIONSHIPS_FILE=Acrogymnospermae-protein-sequences-relationships.csv
    IDENTITIES_FILE=Acrogymnospermae-protein-sequences-identities.csv
    CONSEQS_FILE=Acrogymnospermae-protein-sequences-consensus.fasta

    THREADS=16

else
    echo 'Environment error'; exit 3
fi

FASTA_PATH=$DATA_DIR/$FASTA_FILE

PATH=$NGSHELPER_DIR:$MMSEQS2_DIR:$PATH

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

function test_loop
{

    for I in "${S[@]}"; do
        for J in "${C[@]}"; do
            for K in "${MSI[@]}"; do

                STEP_INIT_DATETIME=`date +%s`

                echo "$SEP"
                echo "$SEP"
                echo "$SEP"
                echo "TEST PARAMETERS - S: $I - C: $J- MSI: $K"

                OUTPUT_DIR=$TEST_DIR/`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`-S$I-C$J-MSI$K-$ALIGNER
                OUTPUT_PREFIX=$OUTPUT_DIR/`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
                CLUSTER_DIR=$OUTPUT_DIR/clusters
                ALLSEQS_PATH=$OUTPUT_DIR/$ALLSEQS_FILE
                RELATIONSHIPS_PATH=$OUTPUT_DIR/$RELATIONSHIPS_FILE
                IDENTITIES_PATH=$OUTPUT_DIR/$IDENTITIES_FILE
                CONSEQS_PATH=$OUTPUT_DIR/$CONSEQS_FILE

                if [ -d "$OUTPUT_DIR" ]; then rm -rf $OUTPUT_DIR; fi; mkdir --parents $OUTPUT_DIR 
                if [ -d "$CLUSTER_DIR" ]; then rm -rf $CLUSTER_DIR; fi; mkdir --parents $CLUSTER_DIR

                cluster_sequences $OUTPUT_PREFIX $I $J $K
                split_clusters $ALLSEQS_PATH $RELATIONSHIPS_PATH $CLUSTER_DIR
                align_clusters $CLUSTER_DIR
                calculate_clusters_identity $CLUSTER_DIR $IDENTITIES_PATH
                calculate_consensus_seqs $CLUSTER_DIR
                unify_consensus_seqs $CLUSTER_DIR $CONSEQS_PATH

                STEP_END_DATETIME=`date +%s`

                DURATION=`expr $STEP_END_DATETIME - $STEP_INIT_DATETIME`
                HH=`expr $DURATION / 3600`
                MM=`expr $DURATION % 3600 / 60`
                SS=`expr $DURATION % 60`
                FORMATTED_DURATION=`printf "%03d:%02d:%02d\n" $HH $MM $SS`

                echo "$SEP"
                echo "TOTAL STEP TIME: $DURATION s ($FORMATTED_DURATION)."

            done
        done
    done

}

#-------------------------------------------------------------------------------

function cluster_sequences
{

    echo "$SEP"
    echo 'Clusterint sequences ...'
    echo "$1 - $2 - $4 - $FASTA_PATH"
    /usr/bin/time \
        mmseqs \
            easy-cluster \
            $FASTA_PATH \
            $1 \
            tmp \
            --threads $THREADS \
            -s $2 \
            -c $3 \
            --cov-mode $CM \
            --min-seq-id $4 \
            --similarity-type $ST
    RC=$?
    if [ $RC -ne 0 ]; then manage_error mmseqs $RC; fi

}

#-------------------------------------------------------------------------------

function split_clusters
{

    echo "$SEP"
    echo 'Spliting clusters ...'
    /usr/bin/time \
        split-mmseqs2-clusters.py \
            --allseqs=$1 \
            --relationships=$2 \
            --outdir=$3 \
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

    CLUSTERS_FILE_LIST=$1/clusters-files.txt
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
    echo 'Calculating identity percentage of clusters ...'
    /usr/bin/time \
        calculate-alignment-identity.py \
            --indir=$1 \
            --pattern=cluster.*-$ALIGNER.fasta \
            --out=$2 \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-alignment-identity.py $RC; fi

}

#-------------------------------------------------------------------------------

function calculate_consensus_seqs
{

    source activate emboss

    echo "$SEP"

    ALIGNED_CLUSTERS_FILE_LIST=$1/aligned-clusters-files.txt
    find $1 -type f -name cluster*-$ALIGNER.fasta > $ALIGNED_CLUSTERS_FILE_LIST
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
    echo 'Unifying sequences (sequences "cluster.*-$ALIGNER.fasta" used by MMSEQ2-benchmarking) ...'
    /usr/bin/time \
        unify-consensus-seqs.py \
            --indir=$1 \
            --pattern=cluster.*-$ALIGNER.cons.fasta \
            --out=$2 \
            --verbose=N \
            --trace=N
    RC=$?
    if [ $RC -ne 0 ]; then manage_error calculate-alignment-identity.py $RC; fi

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
test_loop
end

#-------------------------------------------------------------------------------
