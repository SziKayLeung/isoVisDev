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
    help = "Loads data from whole_genecounts.csv"

    def handle(self, *args, **options):
    
        # Show this if the data already exist in the database
        if Genecounts.objects.exists():
            print('gene counts data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
            
        # Show this before loading the data into the database
        print("Loading gene counts data")


        #Code to load the data into database
        for row in DictReader(open('./expression/files/NormalisedGeneCounts.csv')):
            Genecount=Genecounts(sampleID=row['sampleID'], geneName=row['geneName'], counts=row['counts'], group=row['group'], sex = row['sex'])  
            Genecount.save()
    
    def __str__(self):
        return self.title
            