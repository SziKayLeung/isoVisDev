import logging
import os
from io import BytesIO

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
    try:
        # Configure S3 client (uses IAM role credentials automatically)
        s3_client = boto3.client("s3")

        bucket_name = "gene-data-bucket"
        object_key = f"parquet/{gene_name}.parquet"

        # Fetch the object from S3 bucket
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        # Read parquet data directly from bytes
        parquet_data = response["Body"].read()
        df = pd.read_parquet(BytesIO(parquet_data))
        return df

    except ClientError as e:
        logger.error(f"Error fetching gene data for {gene_name} from S3 bucket: {e}")

        # Try getting file from local storage as a fallback - this is just for running locally in development
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        parquet_path = os.path.join(
            dir_path, "static", "parquet", f"{gene_name}.parquet"
        )
        try:
            df = pd.read_parquet(parquet_path)
            return df
        except FileNotFoundError:
            logger.error(f"Local parquet file not found for gene {gene_name}")
            raise
        except Exception as local_e:
            logger.error(f"Error reading local gene data for {gene_name}: {local_e}")
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

    # Return JSON instead of HTML
    return fig.to_json()


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

    # Return JSON instead of HTML
    return fig.to_json()
