from csv import DictReader

from django.core.management import BaseCommand

# Import the model
from expression.models import Genecounts

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables

Important to migrate the app first: 
manage.py makemigrations expression
manage.py migrate

# to reload the database
python manage.py load_gene_counts
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from NormalisedGeneCounts.csv"

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if Genecounts.objects.exists():
            print("gene counts data already loaded...exiting.")
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading gene counts data")

        batch_size = 10000  # Adjust this based on your memory
        batch = []

        with open("./expression/files/NormalisedGeneCounts.csv") as csvfile:
            for i, row in enumerate(DictReader(csvfile)):
                batch.append(
                    Genecounts(
                        sampleID=row["sampleID"],
                        geneName=row["geneName"],
                        counts=row["counts"],
                        group=row["group"],
                        sex=row["sex"],
                    )
                )

                if len(batch) >= batch_size:
                    Genecounts.objects.bulk_create(batch)
                    batch = []

                if i % 50000 == 0:
                    print(f"Processed {i} rows...")

            # Don't forget the last batch
            if batch:
                Genecounts.objects.bulk_create(batch)

        print("Loading complete!")

    def __str__(self):
        return self.help
