from rest_framework import viewsets
from rest_framework import serializers
from django.contrib.auth import get_user_model
from recordings.models import Detection, Species, SpeciesImage
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count, Max
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
import flickr_api
from django.conf import settings
from random import choice
from pprint import pprint
import requests
from html import escape
from django.core.files.base import ContentFile
from braces.views import CsrfExemptMixin

User = get_user_model()


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        exclude = []


class SpeciesImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeciesImage
        read_only_fields = ["species", "image", "source_id", "id"]
        exclude = []


class SpeciesImageViewSet(CsrfExemptMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    authentication_classes = []

    queryset = SpeciesImage.objects.all()
    serializer_class = SpeciesImageSerializer


class DetectionSerializer(serializers.ModelSerializer):
    species = SpeciesSerializer()

    class Meta:
        model = Detection
        exclude = [
            "status",
            "recording",
            "extracted_file",
            "extracted",
            "analyzer",
            "analysis",
        ]


class DetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = Detection.objects.all()
    serializer_class = DetectionSerializer


class DailyDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    current_date = timezone.localtime(timezone.now()).date()
    start_of_day = timezone.make_aware(timezone.datetime.combine(current_date, timezone.datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)

    queryset = Detection.objects.filter(detected_at__range=(start_of_day, end_of_day))
    serializer_class = DetectionSerializer


class NowDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    def get_queryset(self):
        recent_minutes_default = settings.KIOSK_DETECTIONS_NOW_MINUTES
        recent_minutes = int(
            self.request.query_params.get("minutes", recent_minutes_default)
        )
        recent_cutoff_time = timezone.now() - timedelta(minutes=recent_minutes)
        queryset = Detection.objects.all().filter(detected_at__gte=recent_cutoff_time)
        return queryset

    serializer_class = DetectionSerializer


class SpeciesCountSerializer(serializers.Serializer):
    common_name = serializers.CharField(source="species__common_name")
    scientific_name = serializers.CharField(source="species__scientific_name")
    id = serializers.IntegerField(source="species__id")
    count = serializers.IntegerField()
    avg_confidence = serializers.FloatField()
    max_confidence = serializers.FloatField()


class DailySpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    def get_queryset(self):
        # Filter the queryset by the date field
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            tz_start_date = timezone.make_aware(
                datetime.combine(start_date_obj, datetime.min.time())
            )

        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            tz_end_date = timezone.make_aware(
                datetime.combine(end_date_obj, datetime.min.time())
            )

        # Look for start_date and end_date.
        query = Detection.objects.all()

        if start_date:
            query = query.filter(detected_at__gte=tz_start_date)

        if end_date:
            tz_end_date = tz_end_date + timedelta(days=1)
            query = query.filter(detected_at__lt=tz_end_date)

        if not start_date and not end_date:
            # Filter just for today using a range to avoid __date function scan.
            today_start = timezone.make_aware(
                datetime.combine(timezone.localtime(timezone.now()).date(), datetime.min.time())
            )
            today_end = today_start + timedelta(days=1)
            query = query.filter(detected_at__range=(today_start, today_end))

        queryset = (
            query.values(
                "species__common_name", "species__scientific_name", "species__id"
            )
            .annotate(count=Count("species"), avg_confidence=Avg("confidence"), max_confidence=Max("confidence"))
            .order_by("-count")
            .distinct()
        )
        return queryset

    serializer_class = SpeciesCountSerializer


class SpeciesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer

    @action(detail=True, methods=["get"])
    def image(self, request, pk=None):
        print("getting a flickr image", pk)
        species = self.get_object()

        species_image_limit = settings.FLICKR_RESULTS_LIMIT_PER_SPECIES
        query = SpeciesImage.objects.filter(species=species, is_active=True)
        if query.count() >= species_image_limit:
            # Use one of the saved images.
            species_image = query.order_by("?").first()
            image_url = species_image.image.url
            return Response(
                {
                    "common_name": species.common_name,
                    "url": image_url,
                    "id": species_image.id,
                }
            )

        flickr_api.set_keys(
            api_key=settings.FLICKR_KEY, api_secret=settings.FLICKR_SECRET
        )
        image_list = flickr_api.Photo.search(
            text=species.common_name,
            content_types=0,
            safe_search=1,
            per_page=10,
            sort="relevance",
        )

        # Select a random of the 10 images.
        image = choice(image_list)

        # Use the Large size or Medium.
        image_url = image.get("sizes", {}).get("Large", {}).get("source")

        if not image_url:
            image_url = image.get("sizes", {}).get("Medium", {}).get("source")

        # image_url = image.get("url_o")
        # if not image_url:
        #     image_url = image.get("url_l")

        # if not image_url:
        #     image_url = image.get("url_c")

        # if not image_url:
        #     image_url = image.get("sizes", {}).get("Original", {}).get("url")

        # if not image_url:
        #     image_url = image.get("sizes", {}).get("Medium", {}).get("url")

        if not image_url:
            pprint(image.__dict__)
            raise NotImplementedError("Need a handler for this exception.")

        response = requests.get(image_url)

        if response.status_code == 200:
            # Cache the image.
            species_image, _ = SpeciesImage.objects.get_or_create(
                species=species,
                source_id=image.get("id"),
                defaults={
                    "image": ContentFile(
                        response.content,
                        name=f"{escape(species.common_name)}-{image.get('id')}.jpg",
                    ),
                },
            )
            image_url = species_image.image.url
            return Response(
                {
                    "common_name": species.common_name,
                    "url": image_url,
                    "id": species_image.id,
                }
            )

        return Response({"common_name": species.common_name, "url": image_url})
