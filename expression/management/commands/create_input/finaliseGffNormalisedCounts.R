library("data.table")
library("dplyr")
library("dplyr")
library("stringr")


topAbundantDTETranscripts="/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/ListOfTopAbundantDTETranscripts.txt"
topAbundantDTETranscripts <- fread(topAbundantDTETranscripts, data.table = F)

normAllCounts="/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/18_deseq/2_DTE/DESeq2_whole_development_normAll.csv"
normAllCounts <- fread(normAllCounts, data.table = F)
transcriptsInterest <- normAllCounts %>% filter(isoform %in% topAbundantDTETranscripts$x)
write.csv(transcriptsInterest, "/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/NormalisedTranscriptCounts_GroupSexDTE_TopAbundant.csv", 
quote = F, row.names = F)

gff_file="/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/10_cpat/WholeTargeted_cpatcdsphased_filtered.gff3"
gff <- read.delim(gff_file, header=F, comment.char="#") 
gff <- gff %>% filter(V3 != "gene")
test_gff <- gff[1:2,]
transcript_ids <- gsub(".*transcript_id=([^;]+).*", "\\1", gff$V9)
gff$transcript_ids <- transcript_ids

gffofInterest <- gff %>% filter(transcript_ids %in% topAbundantDTETranscripts$x)
write.table(gffofInterest[,1:9], "/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/GroupSexDTE_TopAbundant.gff", 
quote = F, row.names = F, col.names = F, sep = "\t")


phenotype <- fread("/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/0_metadata/WholeTargetedphenotype_fixedsex.csv", data.table = F)
counts <- fread("/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/NormalisedTranscriptCounts_GroupSexDTE_TopAbundant.csv", data.table = F)
counts <- merge(counts, phenotype, by = "sample")
final <- counts %>% select(sample, associated_gene, isoform, normalised_counts, group, sex)
colnames(final) <- c("sampleID","geneName","isoform","counts","group","sex")
final$sampleID <- as.numeric(as.factor(final$sampleID))
final$sex <- as.factor(final$sex)
final$group <- as.factor(final$group)
final$counts <- round(final$counts, 2)
write.csv(final, "/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/NormalisedTranscriptCounts.csv", quote = F, row.names = F)

# structural category of transcripts
class.files <- fread("/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/C_Whole_Targeted/9_sqanti_final/sqantifiltered_monoexonicfiltered_2reads2samples_classification_finalversion.txt", data.table = F)
subsetted.class.files <- class.files[class.files$isoform %in% final$isoform,c("isoform","structural_category")]
write.csv(subsetted.class.files, "/lustre/projects/Research_Project-MRC190311/longReadSeq/ONTRNA/SFARI/webResource/NormalisedTranscriptCounts_category.csv", quote = F, row.names = F)
