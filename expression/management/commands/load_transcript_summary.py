from csv import DictReader

from django.core.management import BaseCommand

# Import the model
from expression.models import TranscriptSummary

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the transcript category data and tallied counts from the CSV files,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables

Important to migrate the app first: 
manage.py makemigrations expression
manage.py migrate

# to reload the database
python manage.py load_transcript_summary
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from NormalisedTranscriptCounts_category.csv and NormalisedTranscriptCounts_tallied.csv"

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if TranscriptSummary.objects.exists():
            print("transcript summary data already loaded...exiting.")
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading transcript category and count data")

        # First, load category data into a dictionary
        category_file_path = (
            "./expression/files/NormalisedTranscriptCounts_category.csv"
        )
        count_file_path = "./expression/files/NormalisedTranscriptCounts_tallied.csv"

        # Load category data
        category_data = {}
        print("Loading category data...")
        for row in DictReader(open(category_file_path)):
            isoform = row["isoform"]
            category = row["structural_category"]
            category_data[isoform] = category

        print(f"Loaded {len(category_data)} transcripts from category file")

        # Load count data and create TranscriptSummary objects
        count_data = {}
        missing_in_category = []
        missing_in_count = []

        print("Loading count data and creating database objects...")
        for row in DictReader(open(count_file_path)):
            isoform = row["isoform"]
            count = float(row["n"])
            count_data[isoform] = count

            # Check if this isoform exists in category data
            if isoform in category_data:
                transcript_summary = TranscriptSummary(
                    isoform=isoform, category=category_data[isoform], counts=count
                )
                transcript_summary.save()
            else:
                missing_in_category.append(isoform)

        print(f"Loaded {len(count_data)} transcripts from count file")

        # Check for transcripts in category file but not in count file
        for isoform in category_data:
            if isoform not in count_data:
                missing_in_count.append(isoform)

        # Report any mismatches
        if missing_in_category:
            print(
                f"WARNING: {len(missing_in_category)} transcripts found in count file but not in category file:"
            )
            for isoform in missing_in_category[:10]:  # Show first 10
                print(f"  - {isoform}")
            if len(missing_in_category) > 10:
                print(f"  ... and {len(missing_in_category) - 10} more")

        if missing_in_count:
            print(
                f"WARNING: {len(missing_in_count)} transcripts found in category file but not in count file:"
            )
            for isoform in missing_in_count[:10]:  # Show first 10
                print(f"  - {isoform}")
            if len(missing_in_count) > 10:
                print(f"  ... and {len(missing_in_count) - 10} more")

        created_count = TranscriptSummary.objects.count()
        print(f"Successfully created {created_count} TranscriptSummary objects")

        if not missing_in_category and not missing_in_count:
            print("✓ All transcripts matched between both files")
        else:
            print(
                "⚠ Some transcripts were missing in one file or the other (see warnings above)"
            )

        print("Transcript category and count data loaded successfully")

    def __str__(self):
        return self.help
