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
INTERPROSCAN_DIR=$APPS/InterProScan
DATA_DIR=$GYMNOTOA/data
# AWS
# -- INTERPROSCAN_DIR=/ngscloud2/apps/InterProScan
# -- DATA_DIR=/ngscloud2/gymnotoa/data-test
# -- DATA_DIR=/ngscloud2/gymnotoa/output-test/MMseqs2-Acrogymnospermae-protein-sequences

# -- FASTA_FILE=06-Pinaster-10unigenes.fasta; FASTA_TYPE=n
# -- FASTA_FILE=GOs-FASTAs-03-PEP_sequences.fa; FASTA_TYPE=p
# -- FASTA_FILE=Acrogymnospermae-protein-sequences-seq1000.fasta; FASTA_TYPE=p
# -- FASTA_FILE=Acrogymnospermae-protein-sequences-seq1000_rep_seq.fasta; FASTA_TYPE=p
# -- FASTA_FILE=Acrogymnospermae-protein-sequences-seq1000-consensus-seqs.fasta; FASTA_TYPE=p
FASTA_FILE=cluster000002-mafft_w_cons.fasta; FASTA_TYPE=p
FASTA_PATH=$DATA_DIR/$FASTA_FILE

# local
OUTPUT_DIR=$GYMNOTOA/output/InterProScan-`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`
# AWS
# -- OUTPUT_DIR=/ngscloud2/gymnotoa/output-test/InterProScan-`echo "$(n=${FASTA_FILE##*/}; echo ${n%.*})"`

# ANALYSIS:
#     * AntiFam: Resource of profile-HMMs designed to identify spurious protein predictions.
#     * CDD: Prediction of protein domains and families based on a collection of well-annotated multiple sequence alignment models.
#     * Coils: Prediction of coiled coil regions in proteins.
#     * Gene3D: Structural assignment for whole genes and genomes using the CATH domain structure database.
#     * Hamap: High-quality automated and manual annotation of microbial proteomes.
#     * IGRFAM ¿?
#     * MobiDBLite: Prediction of intrinsically disordered regions in proteins.
#     * NCBIfam
#     * PANTHER: The PANTHER (Protein ANalysis THrough Evolutionary Relationships) Classification System is a unique resource that classifies genes by their functions, using published scientific experimental evidence and evolutionary relationships to predict function even in the absence of direct experimental evidence.
#     * Pfam: A large collection of protein families, each represented by multiple sequence alignments and hidden Markov models (HMMs).
#     * PIRSF: A guiding principle to provide comprehensive and non-overlapping clustering of UniProtKB sequences into a hierarchical order to reflect their evolutionary relationships.
#     * PIRSR: A database of protein families based on hidden Markov models (HMMs) and Site Rules.
#     * PRINTS: A compendium of protein fingerprints - a fingerprint is a group of conserved motifs used to characterise a protein family.
#     * ProSitePatterns: Documentation entries describing protein domains, families and functional sites as well as associated patterns and profiles to identify them.
#     * ProSiteProfiles: Documentation entries describing protein domains, families and functional sites as well as associated patterns and profiles to identify them.
#     * SFLD: A database of protein families based on hidden Markov models (HMMs).
#     * SMART: Identification and analysis of domain architectures based on hidden Markov models (HMMs).
#     * SUPERFAMILY: A database of structural and functional annotations for all proteins and genomes.
#     * TIGRFAM: Protein families based on hidden Markov models (HMMs).
#     * Phobius
#     * TMHMM
COMPLETE_ANALYSIS=AntiFam,CDD,Coils,Gene3D,Hamap,MobiDBLite,NCBIfam,PANTHER,Pfam,PIRSF,PIRSR,PRINTS,ProSitePatterns,ProSiteProfiles,SFLD,SMART,SUPERFAMILY,TIGRFAM,Phobius,TMHMM
CURRENT_ANALYSIS=AntiFam,CDD,Coils,Gene3D,Hamap,MobiDBLite,NCBIfam,PANTHER,Pfam,PIRSF,PIRSR,PRINTS,ProSitePatterns,ProSiteProfiles,SFLD,SMART,SUPERFAMILY,TIGRFAM

ALL_FORMATS=TSV,XML,JSON,GFF3
CURRENT_FORMATS=TSV

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

function run_interscanpro
{

    echo "$SEP"
    echo "Running InterScanPro ..."
    /usr/bin/time \
        $INTERPROSCAN_DIR/interproscan.sh \
            --cpu $NCPUS \
            --input $FASTA_PATH \
            --seqtype $FASTA_TYPE \
            --applications $CURRENT_ANALYSIS \
            --iprlookup \
            --goterms \
            --pathways \
            --formats $CURRENT_FORMATS \
            --output-dir $OUTPUT_DIR
    RC=$?
    if [ $RC -ne 0 ]; then manage_error interproscan.sh $RC; fi

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
run_interscanpro
end

#-------------------------------------------------------------------------------
