# List of required packages
required_packages <- c("ggplot2", "dplyr", "devtools")  
# List of development packages
dev_packages <- c("dzhang32/ggtranscript")

# Install required packages
for (package in required_packages) {
    if (!require(package, character.only = TRUE)) {
        install.packages(package, dependencies = TRUE)
    }
}

#devtools::install_github("dzhang32/ggtranscript")

# packages
suppressMessages(library("ggplot2"))
suppressMessages(library("dplyr"))
suppressMessages(library("ggtranscript"))

args <- commandArgs(trailingOnly = TRUE)
gtfPath <- args[1]
outputPath <- args[2]

#message("Loading gtf for plotting")

plot_simply <- function(gtfPath){

  gtf <- read.table(gtfPath, sep = ",", header = T)
  gexons <- gtf %>% dplyr::filter(feature == "exon")

  print(gexons)

  gexons_rescaled <- shorten_gaps(
  gexons, 
  to_intron(gexons, "isoform"), 
  group_var = "isoform"
  )

  p <- gexons_rescaled %>%
    dplyr::filter(type == "exon") %>%
    ggplot(aes(
        xstart = start,
        xend = end,
        y = isoform
    )) +
    geom_range() +
    geom_intron(
        data = gexons_rescaled %>% dplyr::filter(type == "intron"), 
        arrow.min.intron.length = 200
    ) +
    theme_classic() +
    labs(y = NULL) +
    theme(
    axis.line = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    legend.position = "none",
    panel.background = element_blank(),
    panel.border = element_blank(),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    plot.background = element_blank(),
    )



  return(p)
}

p <- plot_simply(gtfPath)

png(paste0(outputPath, "/static/plots/transcript_plot.png"))
print(p)
dev.off()