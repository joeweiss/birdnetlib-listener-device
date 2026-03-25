from django.urls import path
from recordings.views import DetectionSpeciesListView, LatestExtractionsListView, index, species_list_preview
from recordings.api_views import (
    daily_bird_report,
    get_weather_conditions,
    get_weather_forecast,
    populate_fake_detections,
    close_kiosk,
)

urlpatterns = [
    path("daily.json", daily_bird_report),
    path("api/system/kiosk/close/", close_kiosk),
    path("api/weather/current/", get_weather_conditions),
    path("api/weather/forecast/", get_weather_forecast),
    path("species/<id>/", DetectionSpeciesListView.as_view(), name="detection_species"),
    path("api/testing/populate_detections_now/", populate_fake_detections),
    path("extractions/", LatestExtractionsListView.as_view(), name="latest_extractions"),
    path("species-list/", species_list_preview, name="species_list_preview"),
    path("", index),
]
