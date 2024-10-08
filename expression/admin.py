from django.contrib import admin
from .models import Genesummary, Genecounts, Transcriptcounts, TranscriptFeature
#from import_export.admin import ImportExportModelAdmin
#from .resource import ReportResource  

#class ReportAdmin(ImportExportModelAdmin):
#     resource_class = ReportResource      
#admin.site.register(GeneSummary, ReportAdmin)


@admin.register(Genesummary)
class GenesummaryAdmin(admin.ModelAdmin):
   list_display=['geneName','totalNum','novelNum']

@admin.register(Genecounts)
class GenecountsAdmin(admin.ModelAdmin):
   list_display=['sampleID','geneName','counts', 'group', 'sex']

@admin.register(Transcriptcounts)
class TranscriptcountsAdmin(admin.ModelAdmin):
   list_display=['sampleID','geneName','isoform','counts', 'group', 'sex']

@admin.register(TranscriptFeature)
class TranscriptGtfFeatureAdmin(admin.ModelAdmin):
   list_display=['seqnames', 'geneName', 'isoform', 'start', 'end', 'feature', 'strand']
