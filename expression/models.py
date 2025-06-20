from django.db import models

# to make new model: python manage.py makemigrations, python manage.py migrate

image = models.ImageField(upload_to="img")


class Genesummary(models.Model):
    geneName = models.CharField(max_length=50)
    totalNum = models.PositiveIntegerField()
    novelNum = models.PositiveIntegerField()

    def __str__(self):
        return self.geneName


class Genecounts(models.Model):
    # sampleID created prior from 1...
    sampleID = models.PositiveIntegerField()
    geneName = models.CharField(max_length=50)
    counts = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.CharField(max_length=2)
    sex = models.CharField(max_length=2)

    def __str__(self):
        return self.geneName


class Transcriptcounts(models.Model):
    # sampleID created prior from 1...
    sampleID = models.PositiveIntegerField()
    geneName = models.CharField(max_length=50, blank=True, null=True)
    isoform = models.CharField(max_length=50)
    counts = models.DecimalField(max_digits=10, decimal_places=2)
    group = models.CharField(max_length=2)
    sex = models.CharField(max_length=2)

    def __str__(self):
        return self.isoform


class TranscriptSummary(models.Model):
    isoform = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    counts = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.isoform


# Transcript gtf
class TranscriptFeature(models.Model):
    seqnames = models.CharField(max_length=100)
    geneName = models.CharField(max_length=100)
    isoform = models.CharField(max_length=50)
    start = models.IntegerField()
    end = models.IntegerField()
    feature = models.CharField(max_length=100)
    strand = models.CharField(max_length=1)

    def __str__(self):
        return self.isoform
