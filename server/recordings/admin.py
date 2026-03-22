from django.contrib import admin
from recordings import models as app_models


class RecordingAdmin(admin.ModelAdmin):
    list_display = ["filepath", "analyze_status", "recording_started"]


admin.site.register(app_models.Recording, RecordingAdmin)


class SpeciesAdmin(admin.ModelAdmin):
    pass


admin.site.register(app_models.Species, SpeciesAdmin)


class SpeciesImageAdmin(admin.ModelAdmin):
    list_display = ["species", "source_id", "is_active"]
    list_filter = ["is_active"]


admin.site.register(app_models.SpeciesImage, SpeciesImageAdmin)


class AnalyzerAdmin(admin.ModelAdmin):
    list_display = ["name"]


admin.site.register(app_models.Analyzer, AnalyzerAdmin)


class AnalysisAdmin(admin.ModelAdmin):
    list_display = ["recording", "analyzer"]
    raw_id_fields = ["recording"]


admin.site.register(app_models.Analysis, AnalysisAdmin)


class DetectionAdmin(admin.ModelAdmin):
    list_display = [
        "species",
        "confidence",
        "detected_at",
        "analyzer",
        "extracted_file",
    ]
    list_filter = [
        "detected_at",
        "analyzer",
        "species",
        "extracted",
    ]
    raw_id_fields = ["recording", "analysis"]


admin.site.register(app_models.Detection, DetectionAdmin)


class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "notification_type",
        "detection_type",
        "is_active",
    ]
    list_filter = [
        "is_active",
    ]


admin.site.register(app_models.NotificationConfig, NotificationConfigAdmin)
