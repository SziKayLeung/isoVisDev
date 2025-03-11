library("dplyr")
library("vroom")
library("data.table")

root_dir <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/1_Projects/SFARI/PaperZenodo/"
load(file = paste0(root_dir,"sqanti/sqantifiltered_monoexonicfiltered_2reads2samples.RData"))
ProteinCodingGenes <- read.table(paste0(root_dir, "/utils/protein-coding-genes.txt"))[["V1"]]
phenotype <- fread(paste0(root_dir, "metadata/WholeTargetedphenotype_fixedsex.csv"),data.table=F, stringsAsFactors=F) %>% mutate(time = age)
output_dir <- "C:/Users/sl693/OneDrive - University of Exeter/ExeterPostDoc/2_Scripts/isoVisDev/expression/files"
#normAllTranscripts <- vroom(paste0(root_dir,"DTE/DESeq2_whole_development_normAll.csv"),delim = ",", show_col_types = FALSE)

# take the 20 most abundant transcripts from protein coding genes
top_transcripts <- class.files$glob_SQ_annoGene %>%
  dplyr::filter(associated_gene %in% ProteinCodingGenes) %>%
  group_by(associated_gene) %>%
  arrange(desc(nreads)) %>%
  slice_head(n = 20) 

# take all differentially expressed transcripts
normGroupTranscript <- fread(paste0(root_dir, "webResource/NormalisedGroupTranscriptCounts.csv"))
normSexTranscript <- fread(paste0(root_dir, "webResource/NormalisedSexTranscriptCounts.csv"))
normTranscript <- rbind(normGroupTranscript,normSexTranscript)
normTranscript <- distinct(normTranscript)

# create a txt file of transcripts of interest
write.csv(normTranscript, paste0(paste0(root_dir, "webResource/NormalisedTranscriptGroupSexCounts.csv")), row.names = F, quote = F)
write.table(normTranscript$isoform, paste0(paste0(root_dir, "webResource/ListOfDTETranscripts.txt")), row.names = F, quote = F)
write.table(top_transcripts$isoform, paste0(paste0(root_dir, "webResource/ListOfTopAbundantTranscripts.txt")), row.names = F, quote = F)

TranscriptofInterest <- unique(c(top_transcripts$isoform,normTranscript$isoform))
write.table(TranscriptofInterest, paste0(paste0(root_dir, "webResource/ListOfTopAbundantDTETranscripts.txt")), row.names = F, quote = F)