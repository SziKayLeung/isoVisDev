import os
import time

from django.conf import settings
from django.core.management import BaseCommand, call_command

# Import all models to check counts
from expression.models import Genecounts, Genesummary, Transcriptcounts, TranscriptSummary


class Command(BaseCommand):
    help = "Reset database and load all data: deletes db, runs migrations, loads all data, and reports counts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-confirmation",
            action="store_true",
            help="Skip confirmation prompt for database deletion",
        )

    def handle(self, *args, **options):
        start_time = time.time()

        # Confirmation prompt unless skipped
        if not options["skip_confirmation"]:
            confirm = input(
                "\n⚠️  WARNING: This will DELETE the entire database and reload all data from .csv files!\n"
                "Are you sure you want to continue? Type 'yes' to proceed: "
            )
            if confirm.lower() != "yes":
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return

        self.stdout.write(self.style.WARNING("\n🔄 Starting database reset and data loading process..."))

        # Step 1: Delete the database file
        self.stdout.write("\n📝 Step 1: Deleting database...")
        db_path = os.path.join(settings.BASE_DIR, "db.sqlite3")
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS(f"✅ Database deleted: {db_path}"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Database file not found, continuing..."))

        # Step 2: Run migrations
        self.stdout.write("\n📝 Step 2: Running migrations...")
        try:
            call_command("makemigrations", "expression", verbosity=0)
            call_command("migrate", verbosity=1)
            self.stdout.write(self.style.SUCCESS("✅ Migrations completed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Migration failed: {e}"))
            return

        # Step 3: Load all data
        loading_commands = [
            ("load_summary_gene", "Gene Summary"),
            ("load_gene_counts", "Gene Counts"),
            ("load_transcript_counts", "Transcript Counts"),
            ("load_transcript_summary", "Transcript Summary"),
        ]

        self.stdout.write("\n📝 Step 3: Loading data...")

        for command, description in loading_commands:
            self.stdout.write(f"\n🔄 Loading {description}...")
            self.stdout.write("-" * 60)
            load_start = time.time()

            try:
                # Use verbosity=2 to ensure all output is shown
                call_command(command, verbosity=2)
                load_time = time.time() - load_start
                self.stdout.write("-" * 60)
                self.stdout.write(self.style.SUCCESS(f"✅ {description} loaded in {load_time:.2f} seconds"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Failed to load {description}: {e}"))
                continue

        # Step 4: Check and report counts
        self.stdout.write("\n📝 Step 4: Checking data counts...")

        models_to_check = [
            (Genesummary, "Gene Summary"),
            (Genecounts, "Gene Counts"),
            (Transcriptcounts, "Transcript Counts"),
            (TranscriptSummary, "Transcript Summary"),
        ]

        total_records = 0
        self.stdout.write(self.style.SUCCESS("\n📊 FINAL DATA COUNTS:"))
        self.stdout.write("=" * 50)

        for model, name in models_to_check:
            try:
                count = model.objects.count()
                total_records += count
                self.stdout.write(f"  {name:20}: {count:>10,} records")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  {name:20}: Error counting - {e}"))

        self.stdout.write("=" * 50)
        self.stdout.write(f"  {'TOTAL':20}: {total_records:>10,} records")

        # Final summary
        total_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Database reset and loading completed in {total_time:.2f} seconds!"))

        # Performance summary
        self.stdout.write("\n📈 PERFORMANCE SUMMARY:")
        self.stdout.write(f"  Total time: {total_time:.2f} seconds")
        self.stdout.write(f"  Total records: {total_records:,}")
        if total_time > 0:
            self.stdout.write(f"  Records/second: {total_records / total_time:,.0f}")

    def __str__(self):
        return self.help
