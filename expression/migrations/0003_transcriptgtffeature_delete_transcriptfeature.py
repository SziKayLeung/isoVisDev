# Generated by Django 5.1.1 on 2024-09-23 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expression', '0002_transcriptfeature'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranscriptGtfFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seqname', models.CharField(max_length=100)),
                ('feature', models.CharField(max_length=100)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('strand', models.CharField(max_length=1)),
                ('gene_id', models.CharField(max_length=100)),
                ('transcript_id', models.CharField(max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='TranscriptFeature',
        ),
    ]
