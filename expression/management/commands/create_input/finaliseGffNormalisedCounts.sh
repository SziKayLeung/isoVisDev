#!/bin/bash
#SBATCH --export=ALL # export all environment variables to the batch job
#SBATCH -D . # set working directory to .
#SBATCH -p mrcq # submit to the parallel queue
#SBATCH --time=20:00:00 # maximum walltime for the job
#SBATCH -A Research_Project-MRC148213 # research project to submit under
#SBATCH --nodes=1 # specify number of nodes
#SBATCH --ntasks-per-node=16 # specify number of processors per node
#SBATCH --mail-type=END # send email at job completion
#SBATCH --mail-user=sl693@exeter.ac.uk # email address


# create input files for resource
outputDir=/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/
topAbundantDTETranscripts=${outputDir}/ListOfTopAbundantDTETranscripts.txt
normAllCounts=/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/18_deseq/2_DTE/DESeq2_whole_development_normAll.csv
grep -w -f ${topAbundantDTETranscripts} ${normAllCounts} > ${outputDir}/NormalisedTranscriptCounts_GroupSexDTE_TopAbundant.csv

gff=/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/10_cpat/WholeTargeted_cpatcdsphased_filtered.gff3
grep -w -f ${topAbundantDTETranscripts} ${gff} > ${outputDir}/GroupSexDTE_TopAbundant.gff

