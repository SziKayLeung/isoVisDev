import logging
from io import StringIO

import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from botocore.exceptions import ClientError

logger = logging.getLogger("isoVisDev")


def fetch_gene_data_from_s3(gene_name):
    """
    Fetch gene data from AWS S3 bucket.

    Args:
        gene_name (str): The name of the gene to fetch data for

    Returns:
        pd.DataFrame: The gene data as a pandas DataFrame
    """
    # # Temporary fallback to local files until S3 is configured
    # dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # gtfPath = os.path.join(dir_path, "static", f"{gene_name}.txt")

    # try:
    #     df = pd.read_csv(gtfPath, sep="\t")
    #     return df
    # except FileNotFoundError:
    #     logger.error(f"Gene data file not found for {gene_name}")
    #     raise
    # except Exception as e:
    #     logger.error(f"Error reading gene data for {gene_name}: {e}")
    #     raise

    try:
        # Configure S3 client (uses IAM role credentials automatically)
        s3_client = boto3.client("s3")

        # Define your bucket and key
        bucket_name = "gene-data-bucket"
        object_key = f"static/{gene_name}.txt"

        # Fetch the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = response["Body"].read().decode("utf-8")

        # Convert to DataFrame
        df = pd.read_csv(StringIO(content), sep="\t")
        return df

    except ClientError as e:
        logger.error(f"Error fetching gene data for {gene_name} from S3: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching gene data for {gene_name}: {e}")
        raise


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


def transript_visualisation(gene_name, transcript):
    df = fetch_gene_data_from_s3(gene_name)

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
        xaxis_title="Genomic Position",
        yaxis_title="Transcript ID",
        yaxis=dict(tickmode="array", tickvals=transcripts, ticktext=transcripts),
        showlegend=False,
        height=240,
        plot_bgcolor="white",
    )

    fig = fig.to_html()
    return fig
