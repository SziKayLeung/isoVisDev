# Generated by Django 5.1.1 on 2024-09-26 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expression', '0006_rename_seqname_transcriptfeature_seqnames'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Film',
        ),
        migrations.DeleteModel(
            name='Genre',
        ),
    ]
