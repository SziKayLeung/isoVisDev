from csv import DictReader

from django.core.management import BaseCommand

# Import the model
from expression.models import TranscriptCategory

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the transcript category data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables

Important to migrate the app first: 
manage.py makemigrations expression
manage.py migrate

# to reload the database
python manage.py load_transcript_category
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from NormalisedTranscriptCounts_category.csv"

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if TranscriptCategory.objects.exists():
            print("transcript category data already loaded...exiting.")
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading transcript category data")

        # Code to load the data into database
        for row in DictReader(
            open("./expression/files/NormalisedTranscriptCounts_category.csv")
        ):
            transcript_category = TranscriptCategory(
                isoform=row["isoform"],
                category=row["structural_category"],
            )
            transcript_category.save()

        print("Transcript category data loaded successfully")

    def __str__(self):
        return self.help
