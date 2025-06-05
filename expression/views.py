import os

import pandas as pd
from django.shortcuts import render

from .forms import GeneForm, TheForm
from .models import Genecounts, Genesummary, Transcriptcounts
from .utils.plotting import gene_boxplot, transript_visualisation


# Home tab
def home(request):
    return render(request, "home.html")


# Summary tab
def summary(request):
    form = GeneForm()
    context = {"form": form, "title": "Gene Search and Details"}

    if request.method == "POST":
        genename = request.POST.get("genename")
        request.session["genename"] = genename

        try:
            gene = Genesummary.objects.get(geneName=genename)

            # gene expression
            queryset = Genecounts.objects.filter(geneName=genename)
            data = list(queryset.values())
            df = pd.DataFrame(data)
            fig = gene_boxplot(df)

            context.update({"gene": gene, "plot": fig, "show_results": True})

        except Genesummary.DoesNotExist:
            # Handle case where gene is not found
            context.update(
                {
                    "error_message": f"{genename} not found in our dataset",
                    "show_results": False,
                }
            )

    return render(request, "expression/gene_level.html", context)


# Transcript level tab
def transcript_identify(request):
    context = {
        "gene_form": GeneForm(),
        "show_transcript_form": False,
        "show_results": False,
        "error_message": None,
    }

    if request.method == "POST":
        # Check if the user submitted the gene form
        if "gene_name" in request.POST:
            gene_form = GeneForm(request.POST)
            if gene_form.is_valid():
                gene_name = gene_form.cleaned_data["gene_name"]
                transcripts = Transcriptcounts.objects.filter(geneName=gene_name)
                unique_transcripts = {
                    transcript.isoform: transcript for transcript in transcripts
                }.values()

                if transcripts.exists():
                    # Create choices for the dropdown based on the fetched transcripts
                    transcript_choices = [
                        (t.isoform, t.isoform) for t in unique_transcripts
                    ]
                    print("Available transcript choices:", transcript_choices)

                    # Initialize the multiple selection form with transcript choices
                    transcript_form = TheForm()  # No POST data here
                    transcript_form.fields["Transcripts"].choices = transcript_choices

                    # Store gene_name in session for later use
                    request.session["gene_name"] = gene_name

                    # Update context to show transcript selection form
                    context.update(
                        {
                            "gene_form": gene_form,
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                        }
                    )

                else:
                    # If no transcripts found for the gene
                    context.update(
                        {
                            "gene_form": gene_form,
                            "error_message": f"No transcripts found for gene {gene_name}",
                        }
                    )

        # Check if the user submitted the transcript selection form
        else:
            transcript_form = TheForm(request.POST)
            gene_name = request.session.get("gene_name")

            # Re-fetch transcripts based on the stored gene_name
            transcripts = Transcriptcounts.objects.filter(geneName=gene_name)
            unique_transcripts = {
                transcript.isoform: transcript for transcript in transcripts
            }.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form.fields["Transcripts"].choices = transcript_choices

            if transcript_form.is_valid():
                selected_transcripts = transcript_form.cleaned_data["Transcripts"]

                # transcript structure
                dir_path = os.path.dirname(os.path.realpath(__file__))
                gtfPath = os.path.join(dir_path, "static", f"{gene_name}.txt")
                print(gtfPath)
                plotStructure = transript_visualisation(
                    gtfPath, selected_transcripts[0]
                )

                # boxplot
                selected_transcript_expression_df = Transcriptcounts.objects.filter(
                    isoform=selected_transcripts[0]
                )
                expression_df = pd.DataFrame(
                    list(selected_transcript_expression_df.values())
                )
                plotExpression = gene_boxplot(expression_df)

                print("Selected transcripts:", selected_transcripts)

                # Update context to show both transcript form and results
                context.update(
                    {
                        "gene_form": GeneForm(),
                        "transcript_form": transcript_form,
                        "selected_transcripts": selected_transcripts,
                        "plotStructure": plotStructure,
                        "plotExpression": plotExpression,
                        "gene_name": gene_name,
                        "show_transcript_form": True,
                        "show_results": True,
                    }
                )
            else:
                print("Form is not valid:", transcript_form.errors)
                context.update(
                    {
                        "gene_form": GeneForm(),
                        "transcript_form": transcript_form,
                        "gene_name": gene_name,
                        "show_transcript_form": True,
                        "error_message": "Please select at least one transcript.",
                    }
                )

    return render(request, "expression/transcript_level.html", context)
