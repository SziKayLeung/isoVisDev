from csv import DictReader

from django.core.management import BaseCommand

# Import the model
from expression.models import TranscriptCategory

ALREADY_LOADED_ERROR_MESSAGE = """
If you need to reload the transcript category data from the CSV file,
you can clear just this table's data using:
python manage.py shell
>>> from expression.models import TranscriptCategory
>>> TranscriptCategory.objects.all().delete()

Then run this command again:
python manage.py load_transcript_category

Important: Before first use, make sure to create and apply migrations:
python manage.py makemigrations expression
python manage.py migrate
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
