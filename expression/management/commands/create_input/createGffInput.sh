#!/bin/bash
#SBATCH --export=ALL # export all environment variables to the batch job
#SBATCH -D . # set working directory to .
#SBATCH -p mrcq # submit to the parallel queue
#SBATCH --time=144:00:00 # maximum walltime for the job
#SBATCH -A Research_Project-MRC148213 # research project to submit under
#SBATCH --nodes=1 # specify number of nodes
#SBATCH --ntasks-per-node=16 # specify number of processors per node
#SBATCH --mail-type=END # send email at job completion
#SBATCH --mail-user=sl693@exeter.ac.uk # email address

module load R/4.2.2-foss-2022b

gencodeAnnotation=/lustre/projects/Research_Project-MRC148213/lsl693/references/human/gencode.v40.annotation.gff3
cpatCDS=/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/10_cpat/LRBrain_QCed_CPAT_CDS_wholetargeted_phasefixed.gff3
outputGffs=/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/gffs
createGffFinalTable=/lustre/projects/Research_Project-MRC148213/lsl693/scripts/isoVisDev/expression/management/commands/create_input/createGffFinalTable.R
finalOutputDir=/lustre/projects/Research_Project-MRC148213/lsl693/scripts/isoVisDev/expression/static/

while IFS=$'\t' read -r col1 col2 col3; do
  	gene_symbol="$col1"
  	transcript_id=$(echo "${col2}" | cut -d'.' -f1)
  	ensembl="$col2"
  	echo ${gene_symbol}	
	echo ${transcript_id}
	
	grep -w ${ensembl} ${gencodeAnnotation} > ${outputGffs}/${gene_symbol}_mane_gencode.gff3 
	grep -w ${gene_symbol} ${cpatCDS} > ${outputGffs}/${gene_symbol}.gff3 
	Rscript $createGffFinalTable ${outputGffs}/${gene_symbol}_mane_gencode.gff3 ${outputGffs}/${gene_symbol}.gff3 ${finalOutputDir} ${gene_symbol} 
	
done < /lustre/projects/Research_Project-MRC148213/lsl693/scripts/isoVisDev/expression/management/commands/create_input/MANE_protein-coding-genes_nonMT.txt


