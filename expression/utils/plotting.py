import logging

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger("isoVisDev")


def gene_boxplot(df):
    fig = px.box(
        data_frame=df,
        x="group",
        y="counts",
        color="sex",
        template="simple_white",
        labels={"group": "Group", "counts": "Normalised expression"},
    )

    fig = fig.to_html()
    return fig


def transript_visualisation(gtfPath, transcript):
    # Read shorten_gaps df
    df = pd.read_csv(gtfPath, sep="\t")

    # Only plot a few transcripts
    # to_plot=["ONT17_2060_1262" ,"ONT17_2060_3082" ,"ONT17_2060_2166" ,"ONT17_2060_4043"]

    # Extract transcripts to plot and reference transcripts
    df = df[(df["transcript_id"] == transcript) | (df["transcript_id"].str[0] == "E")]

    # Create a plotly figure
    fig = go.Figure()

    # Group data by transcript_id and plot each type of feature (UTR, CDS, Intron) as rectangles
    transcripts = df["transcript_id"].unique()

    for transcript in transcripts:
        transcript_data = df[df["transcript_id"] == transcript]

        # Add rectangles for each feature type
        for _, row in transcript_data.iterrows():
            if row["type"] == "UTR":
                color = "orange"
                width = 5
            elif row["type"] == "CDS":
                color = "blue"
                width = 10
            else:
                color = "grey"
                width = 1
            fig.add_trace(
                go.Scatter(
                    x=[row["start"], row["end"]],
                    y=[transcript, transcript],
                    mode="lines",
                    line=dict(width=width, color=color),
                    showlegend=False,
                )
            )

    # Update layout to make the plot clearer
    fig.update_layout(
        # title="ACTG1",
        xaxis_title="Genomic Position",
        yaxis_title="Transcript ID",
        yaxis=dict(tickmode="array", tickvals=transcripts, ticktext=transcripts),
        showlegend=False,
        height=240,
        plot_bgcolor="white",
    )

    fig = fig.to_html()
    return fig
