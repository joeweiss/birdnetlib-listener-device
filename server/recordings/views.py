from datetime import datetime

from django.conf import settings
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, HttpResponse, render

from recordings.models import Detection, Species


class DetectionSpeciesListView(ListView):
    template_name = "recordings/detection_by_species_list.html"
    context_object_name = "detections"

    def get_queryset(self):
        self.species = get_object_or_404(Species, id=self.kwargs["id"])
        return Detection.objects.filter(species=self.species).order_by("-detected_at")[
            0:30
        ]

    def get_context_data(self, **kwargs):
        context = super(DetectionSpeciesListView, self).get_context_data(**kwargs)
        context["species"] = self.species
        return context


class LatestExtractionsListView(ListView):
    template_name = "recordings/latest_extractions.html"
    context_object_name = "detections"
    paginate_by = 25

    def get_queryset(self):
        return Detection.objects.filter(extracted=True).order_by("-detected_at").select_related("species")


def species_list_preview(request):
    from birdnetlib.species import SpeciesList

    lat = settings.LATITUDE
    lon = settings.LONGITUDE
    default_threshold = 0.03
    threshold = float(request.GET.get("threshold", default_threshold))
    today = datetime.now()

    species = SpeciesList()
    results = species.return_list(
        lon=lon,
        lat=lat,
        date=today,
        threshold=threshold,
    )

    threshold_options = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]

    return render(request, "recordings/species_list_preview.html", {
        "lat": lat,
        "lon": lon,
        "date": today,
        "threshold": threshold,
        "default_threshold": default_threshold,
        "species_list": results,
        "species_count": len(results),
        "threshold_options": threshold_options,
    })


def index(request):
    return HttpResponse("Hello, World!")
