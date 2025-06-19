#!/usr/bin/env python3
"""
Script to convert all .txt files in the static directory to .parquet format.
This will significantly reduce file sizes and improve loading performance.
"""

import logging
from pathlib import Path

import pandas as pd

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def convert_txt_to_parquet(static_dir):
    """
    Convert all .txt files in static directory to .parquet format.

    Args:
        static_dir (str): Path to the static directory containing .txt files
    """
    static_path = Path(static_dir)

    if not static_path.exists():
        logger.error(f"Static directory does not exist: {static_dir}")
        return

    # Create parquet subdirectory
    parquet_dir = static_path / "parquet"
    parquet_dir.mkdir(exist_ok=True)
    logger.info(f"Created parquet directory: {parquet_dir}")

    # Find all .txt files
    txt_files = list(static_path.glob("*.txt"))
    total_files = len(txt_files)

    if total_files == 0:
        logger.warning("No .txt files found in the static directory")
        return

    logger.info(f"Found {total_files} .txt files to convert")

    # Track conversion statistics
    converted_count = 0
    error_count = 0
    total_original_size = 0
    total_parquet_size = 0

    for i, txt_file in enumerate(txt_files, 1):
        try:
            # Get original file size
            original_size = txt_file.stat().st_size
            total_original_size += original_size

            # Read the tab-separated file
            df = pd.read_csv(txt_file, sep="\t")

            # Create parquet filename
            parquet_file = parquet_dir / f"{txt_file.stem}.parquet"

            # Save as parquet
            df.to_parquet(parquet_file, index=False, engine="pyarrow")

            # Get new file size
            parquet_size = parquet_file.stat().st_size
            total_parquet_size += parquet_size

            # Calculate compression ratio
            compression_ratio = (1 - parquet_size / original_size) * 100

            converted_count += 1

            # Log progress every 100 files or for the first/last few files
            if i <= 5 or i % 100 == 0 or i >= total_files - 5:
                logger.info(
                    f"[{i}/{total_files}] Converted {txt_file.name} "
                    f"({original_size:,} -> {parquet_size:,} bytes, "
                    f"{compression_ratio:.1f}% smaller)"
                )

        except Exception as e:
            logger.error(f"Error converting {txt_file.name}: {str(e)}")
            error_count += 1

    # Print summary statistics
    overall_compression = (
        (1 - total_parquet_size / total_original_size) * 100
        if total_original_size > 0
        else 0
    )

    logger.info("=" * 60)
    logger.info("CONVERSION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Successfully converted: {converted_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(
        f"Original total size: {total_original_size:,} bytes ({total_original_size / 1024 / 1024:.1f} MB)"
    )
    logger.info(
        f"Parquet total size: {total_parquet_size:,} bytes ({total_parquet_size / 1024 / 1024:.1f} MB)"
    )
    logger.info(f"Overall compression: {overall_compression:.1f}% smaller")
    logger.info(
        f"Space saved: {(total_original_size - total_parquet_size):,} bytes ({(total_original_size - total_parquet_size) / 1024 / 1024:.1f} MB)"
    )


def main():
    """Main function to run the conversion."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    static_dir = script_dir.parent / "expression" / "static"

    logger.info(f"Starting conversion in directory: {static_dir}")

    if not static_dir.exists():
        logger.error(f"Static directory not found: {static_dir}")
        logger.info(
            "Please make sure you're running this script from the project root directory."
        )
        return

    try:
        convert_txt_to_parquet(static_dir)
        logger.info("Conversion completed successfully!")
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")


if __name__ == "__main__":
    main()
