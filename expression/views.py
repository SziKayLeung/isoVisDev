import pandas as pd
from django.shortcuts import render

from .forms import GeneForm, TheForm
from .models import Genecounts, Genesummary, Transcriptcounts, TranscriptSummary
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
        # Handle gene search OR filter action (they do the same thing)
        if request.POST.get("filter_action") == "filter" or "gene_name" in request.POST:
            # Get gene name from form or session
            if "gene_name" in request.POST:
                gene_form = GeneForm(request.POST)
                if not gene_form.is_valid():
                    return render(request, "expression/transcript_level.html", context)
                gene_name = gene_form.cleaned_data["gene_name"]
                request.session["gene_name"] = gene_name
            else:
                gene_name = request.session.get("gene_name")
                if not gene_name:
                    return render(request, "expression/transcript_level.html", context)

            # Get selected categories
            category_mapping = {
                "filter_fsm": "FSM",
                "filter_ism": "ISM",
                "filter_nic": "NIC",
                "filter_nnc": "NNC",
                "filter_gg": "GG",
            }

            selected_categories = []
            for filter_name, category_code in category_mapping.items():
                if request.POST.get(filter_name):
                    selected_categories.append(category_code)

            # Default to all categories if none selected and this is initial gene search
            if not selected_categories and "gene_name" in request.POST:
                selected_categories = list(category_mapping.values())

            # Get and filter transcripts
            transcripts = Transcriptcounts.objects.filter(geneName=gene_name)

            if not transcripts.exists():
                context.update(
                    {
                        "gene_form": GeneForm(initial={"gene_name": gene_name}),
                        "error_message": f"Gene '{gene_name}' not found in our dataset",
                        "show_transcript_form": False,
                    }
                )
                return render(request, "expression/transcript_level.html", context)

            # Get the slider value for count threshold
            counts_threshold = request.POST.get("counts_threshold", "0")
            try:
                counts_threshold = float(counts_threshold)
            except ValueError:
                counts_threshold = 0.0

            # Store for the template
            request.session["counts_threshold"] = counts_threshold

            # Filter by category
            if selected_categories:
                # First get isoforms that match the category filter
                filtered_isoforms = TranscriptSummary.objects.filter(
                    category__in=selected_categories
                )

                # Then further filter by the count threshold
                if counts_threshold > 0:
                    filtered_isoforms = filtered_isoforms.filter(
                        counts__gte=counts_threshold
                    )

                # Get just the isoform names
                filtered_isoform_names = filtered_isoforms.values_list(
                    "isoform", flat=True
                )

                # Finally filter transcripts
                transcripts = transcripts.filter(isoform__in=filtered_isoform_names)
            else:
                transcripts = transcripts.none()

            # Create transcript form
            unique_transcripts = {t.isoform: t for t in transcripts}.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form = TheForm()
            transcript_form.fields["Transcripts"].choices = transcript_choices

            # Store in session
            request.session["selected_categories"] = selected_categories

            context.update(
                {
                    "gene_form": GeneForm(initial={"gene_name": gene_name}),
                    "transcript_form": transcript_form,
                    "gene_name": gene_name,
                    "show_transcript_form": True,
                    "selected_categories": selected_categories,
                    "counts_threshold": counts_threshold,
                }
            )

        # Handle transcript selection
        else:
            transcript_form = TheForm(request.POST)
            gene_name = request.session.get("gene_name")
            selected_categories = request.session.get(
                "selected_categories", ["FSM", "ISM", "NIC", "NNC", "GG"]
            )

            # Get the counts threshold from the session
            counts_threshold = request.session.get("counts_threshold", 0)
            try:
                counts_threshold = float(counts_threshold)
            except ValueError:
                counts_threshold = 0.0

            # Re-fetch transcripts for form validation
            transcripts = Transcriptcounts.objects.filter(geneName=gene_name)
            if selected_categories:
                # First get isoforms that match the category filter
                filtered_isoforms = TranscriptSummary.objects.filter(
                    category__in=selected_categories
                )

                # Then further filter by the count threshold
                if counts_threshold > 0:
                    filtered_isoforms = filtered_isoforms.filter(
                        counts__gte=counts_threshold
                    )

                # Get just the isoform names
                filtered_isoform_names = filtered_isoforms.values_list(
                    "isoform", flat=True
                )

                # Finally filter transcripts
                transcripts = transcripts.filter(isoform__in=filtered_isoform_names)

            unique_transcripts = {t.isoform: t for t in transcripts}.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form.fields["Transcripts"].choices = transcript_choices

            base_context = {
                "gene_form": GeneForm(),
                "transcript_form": transcript_form,
                "gene_name": gene_name,
                "show_transcript_form": True,
                "selected_categories": selected_categories,
                "counts_threshold": counts_threshold,
            }

            if transcript_form.is_valid():
                selected_transcripts = transcript_form.cleaned_data["Transcripts"]

                if not selected_transcripts:
                    base_context["error_message"] = (
                        "Please select at least one transcript."
                    )
                    context.update(base_context)
                else:
                    # Generate plots
                    plotStructure = transript_visualisation(
                        gene_name, selected_transcripts[0]
                    )
                    selected_transcript_expression_df = Transcriptcounts.objects.filter(
                        isoform=selected_transcripts[0]
                    )
                    expression_df = pd.DataFrame(
                        list(selected_transcript_expression_df.values())
                    )
                    plotExpression = gene_boxplot(expression_df)

                    base_context.update(
                        {
                            "selected_transcripts": selected_transcripts,
                            "plotStructure": plotStructure,
                            "plotExpression": plotExpression,
                            "show_results": True,
                        }
                    )
                    context.update(base_context)
            else:
                base_context["error_message"] = "Please select at least one transcript."
                context.update(base_context)

    return render(request, "expression/transcript_level.html", context)
