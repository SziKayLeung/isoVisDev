import pandas as pd
from django.shortcuts import render

from .forms import GeneForm, TheForm
from .models import Genecounts, Genesummary, TranscriptCategory, Transcriptcounts
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


def transcript_identify(request):
    context = {
        "gene_form": GeneForm(),
        "show_transcript_form": False,
        "show_results": False,
        "error_message": None,
    }

    if request.method == "POST":
        # Check if this is a filter action (updating transcript list based on category filters)
        if request.POST.get("filter_action") == "filter":
            gene_name = request.session.get("gene_name")
            if gene_name:
                # Get selected category filters
                selected_categories = []
                category_mapping = {
                    "filter_fsm": "FSM",
                    "filter_ism": "ISM",
                    "filter_nic": "NIC",
                    "filter_nnc": "NNC",
                    "filter_gg": "GG",
                }

                for filter_name, category_code in category_mapping.items():
                    if request.POST.get(filter_name):
                        selected_categories.append(category_code)

                # Get filtered transcripts
                transcripts = Transcriptcounts.objects.filter(geneName=gene_name)
                if selected_categories:
                    filtered_isoforms = TranscriptCategory.objects.filter(
                        category__in=selected_categories
                    ).values_list("isoform", flat=True)
                    transcripts = transcripts.filter(isoform__in=filtered_isoforms)
                else:
                    # If no categories selected, show no transcripts
                    transcripts = transcripts.none()

                unique_transcripts = {
                    transcript.isoform: transcript for transcript in transcripts
                }.values()

                if transcripts.exists():
                    transcript_choices = [
                        (t.isoform, t.isoform) for t in unique_transcripts
                    ]
                    transcript_form = TheForm()
                    transcript_form.fields["Transcripts"].choices = transcript_choices

                    # Update session with new categories
                    request.session["selected_categories"] = selected_categories

                    context.update(
                        {
                            "gene_form": GeneForm(initial={"gene_name": gene_name}),
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                            "selected_categories": selected_categories,
                        }
                    )
                else:
                    # If no transcripts found, show empty transcript form without error
                    transcript_form = TheForm()
                    transcript_form.fields["Transcripts"].choices = []

                    context.update(
                        {
                            "gene_form": GeneForm(initial={"gene_name": gene_name}),
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                            "selected_categories": selected_categories,
                        }
                    )

        # Check if the user submitted the gene form
        elif "gene_name" in request.POST:
            gene_form = GeneForm(request.POST)
            if gene_form.is_valid():
                gene_name = gene_form.cleaned_data["gene_name"]

                # Get selected category filters (default to all for initial search)
                selected_categories = []
                category_mapping = {
                    "filter_fsm": "FSM",
                    "filter_ism": "ISM",
                    "filter_nic": "NIC",
                    "filter_nnc": "NNC",
                    "filter_gg": "GG",
                }

                for filter_name, category_code in category_mapping.items():
                    if request.POST.get(filter_name):
                        selected_categories.append(category_code)

                # If this is initial gene search (no checkboxes in POST), default to all categories
                checkbox_in_post = any(
                    request.POST.get(filter_name)
                    for filter_name in category_mapping.keys()
                )
                if not checkbox_in_post:
                    selected_categories = list(category_mapping.values())

                # Get transcripts for the gene
                transcripts = Transcriptcounts.objects.filter(geneName=gene_name)

                # Filter transcripts by category if TranscriptCategory data exists
                if selected_categories:
                    # Get isoforms that match the selected categories
                    filtered_isoforms = TranscriptCategory.objects.filter(
                        category__in=selected_categories
                    ).values_list("isoform", flat=True)

                    # Filter transcripts to only include those with matching categories
                    transcripts = transcripts.filter(isoform__in=filtered_isoforms)
                else:
                    # If no categories selected, show no transcripts
                    transcripts = transcripts.none()

                unique_transcripts = {
                    transcript.isoform: transcript for transcript in transcripts
                }.values()

                if transcripts.exists():
                    # Create choices for the dropdown based on the filtered transcripts
                    transcript_choices = [
                        (t.isoform, t.isoform) for t in unique_transcripts
                    ]
                    print("Available transcript choices:", transcript_choices)

                    # Initialize the multiple selection form with transcript choices
                    transcript_form = TheForm()  # No POST data here
                    transcript_form.fields["Transcripts"].choices = transcript_choices

                    # Store gene_name and selected categories in session for later use
                    request.session["gene_name"] = gene_name
                    request.session["selected_categories"] = selected_categories

                    # Update context to show transcript selection form
                    context.update(
                        {
                            "gene_form": gene_form,
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                            "selected_categories": selected_categories,
                        }
                    )

                else:
                    # If no transcripts found, show empty transcript form without error
                    transcript_form = TheForm()
                    transcript_form.fields["Transcripts"].choices = []

                    context.update(
                        {
                            "gene_form": gene_form,
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                            "selected_categories": selected_categories,
                        }
                    )

        # Check if the user submitted the transcript selection form
        else:
            transcript_form = TheForm(request.POST)
            gene_name = request.session.get("gene_name")
            selected_categories = request.session.get(
                "selected_categories", ["FSM", "ISM", "NIC", "NNC", "GG"]
            )

            # Re-fetch transcripts based on the stored gene_name and categories
            transcripts = Transcriptcounts.objects.filter(geneName=gene_name)

            # Apply category filtering
            if selected_categories:
                filtered_isoforms = TranscriptCategory.objects.filter(
                    category__in=selected_categories
                ).values_list("isoform", flat=True)
                transcripts = transcripts.filter(isoform__in=filtered_isoforms)

            unique_transcripts = {
                transcript.isoform: transcript for transcript in transcripts
            }.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form.fields["Transcripts"].choices = transcript_choices

            if transcript_form.is_valid():
                selected_transcripts = transcript_form.cleaned_data["Transcripts"]

                # Check if transcripts are actually selected for final submission
                if not selected_transcripts:
                    context.update(
                        {
                            "gene_form": GeneForm(),
                            "transcript_form": transcript_form,
                            "gene_name": gene_name,
                            "show_transcript_form": True,
                            "error_message": "Please select at least one transcript.",
                            "selected_categories": selected_categories,
                        }
                    )
                else:
                    # transcript structure
                    plotStructure = transript_visualisation(
                        gene_name, selected_transcripts[0]
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
                            "selected_categories": selected_categories,
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
                        "selected_categories": selected_categories,
                    }
                )

    return render(request, "expression/transcript_level.html", context)
