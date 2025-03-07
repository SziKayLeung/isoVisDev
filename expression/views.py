from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from expression import models
from .models import Genesummary, Genecounts, Transcriptcounts, TranscriptFeature
from .forms import GeneForm, TheForm 
from .utils.plotting import gene_boxplot, run_r_ggtranscript, transript_visualisation
import pandas as pd
import os
import subprocess
import time
import plotly.io as pio
import plotly
import plotly.express as px



# Home tab
def home(request):
    return render(request, 'home.html')

# Summary tab
def summary(request):
    if request.method == 'GET':
        form = GeneForm()
        return render(request, 'expression/select_gene.html', {'form': form})
        
    elif request.method == 'POST':
        genename = request.POST.get('genename')
        request.session['genename'] = genename

        try:
            gene = Genesummary.objects.get(geneName=genename)

            # gene expression
            queryset = Genecounts.objects.filter(geneName=genename)
            data = list(queryset.values())
            df = pd.DataFrame(data)
            fig = gene_boxplot(df)

            context = {
                'title': 'Gene Details Page',
                'gene': gene,
                'plot': fig
            }
            template = 'expression/gene_level.html'

        except Genesummary.DoesNotExist:
            # Handle case where gene is not found
            context = {
                'title': 'Gene Not Found',
                'error_message': f'{genename} not found in our dataset',
            }
            template = 'expression/select_gene.html'

        return render(request,
              template,
              context)


# Transcript level tab
def transcript_identify(request):
    if request.method == 'GET':
        # Display the gene input form
        form = GeneForm()
        return render(request, 'expression/select_transcript_1.html', {'form': form})

    elif request.method == 'POST':
        # Check if the user submitted the gene form
        if 'gene_name' in request.POST:
            gene_form = GeneForm(request.POST)
            if gene_form.is_valid():
                gene_name = gene_form.cleaned_data['gene_name']
                transcripts = TranscriptFeature.objects.filter(geneName=gene_name)
                unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()

                if transcripts.exists():
                    # Create choices for the dropdown based on the fetched transcripts
                    transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
                    print("Available transcript choices:", transcript_choices)

                    # Initialize the multiple selection form with transcript choices
                    transcript_form = TheForm()  # No POST data here
                    transcript_form.fields['Transcripts'].choices = transcript_choices
                    
                    # Store gene_name in session for later use
                    request.session['gene_name'] = gene_name
                    
                    # Render the form with transcript options
                    return render(request, 'expression/select_transcript_2.html', {
                        'form': transcript_form,
                        'gene_name': gene_name
                    })

                else:
                    # If no transcripts found for the gene
                    return render(request, 'expression/select_transcript_1.html', {
                        'form': gene_form,
                        'error_message': f"No transcripts found for gene {gene_name}"
                    })

        # Check if the user submitted the transcript selection form
        else:
            transcript_form = TheForm(request.POST)
            gene_name = request.session.get('gene_name')

            # Re-fetch transcripts based on the stored gene_name
            transcripts = TranscriptFeature.objects.filter(geneName=gene_name)
            unique_transcripts = {transcript.isoform: transcript for transcript in transcripts}.values()
            transcript_choices = [(t.isoform, t.isoform) for t in unique_transcripts]
            transcript_form.fields['Transcripts'].choices = transcript_choices

            if transcript_form.is_valid():
                selected_transcripts = transcript_form.cleaned_data['Transcripts']
                #selected_transcript_df = TranscriptFeature.objects.filter(isoform=selected_transcripts[0])
                #df = pd.DataFrame(selected_transcript_df.values())
                #dir_path = os.path.dirname(os.path.realpath(__file__))
                #gtfPath = os.path.join(dir_path, 'static/plot_df.csv')
                #df.to_csv(gtfPath)

                # transcript structure
                #plot = run_r_ggtranscript(gtfPath)  # Modify this function to accept isoform ID
                #plotStructure = transript_visualisation(df)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                gtfPath = os.path.join(dir_path, 'static', f"{gene_name}.txt")
                print(gtfPath)
                plotStructure = transript_visualisation(gtfPath, selected_transcripts[0])
                #plotStructure_html = pio.to_html(plotStructure)

                # boxplot
                selected_transcript_expression_df = Transcriptcounts.objects.filter(isoform=selected_transcripts[0])
                expression_df = pd.DataFrame(list(selected_transcript_expression_df.values()))
                plotExpression = gene_boxplot(expression_df)

                print("Selected transcripts:", selected_transcripts)
                # Render the success message with selected transcripts
                return render(request, 'expression/transcript_level.html', {
                    'selected_transcripts': selected_transcripts,
                    'plotStructure' : plotStructure,
                    'plotExpression': plotExpression,
                    'gene_name': gene_name
                })
            else:
                print("Form is not valid:", transcript_form.errors)
                return render(request, 'expression/select_transcript_2.html', {
                    'form': transcript_form,
                    'gene_name': gene_name,
                    'error_message': 'Please select at least one transcript.'
                })
