from csv import DictReader

from django.core.management import BaseCommand

# Import the model
from expression.models import Genesummary

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables

# to reload the database
python manage.py load_summary_gene
"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from numGenes.csv"

    def handle(self, *args, **options):
        # Show this if the data already exist in the database
        if Genesummary.objects.exists():
            print("gene summary data already loaded...exiting.")
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading gene summary data")

        batch_size = 10000  # Adjust this based on your memory
        batch = []

        with open("./expression/files/numGenes.csv") as csvfile:
            for i, row in enumerate(DictReader(csvfile)):
                batch.append(
                    Genesummary(geneName=row["associated_gene"], totalNum=row["totalN"], novelNum=row["novelN"])
                )

                if len(batch) >= batch_size:
                    Genesummary.objects.bulk_create(batch)
                    batch = []

                if i % 10000 == 0:
                    print(f"Processed {i} rows...")

            # Don't forget the last batch
            if batch:
                Genesummary.objects.bulk_create(batch)

        print("Loading complete!")

    def __str__(self):
        return self.help
