from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.api.permissions import IsAdminRole
from modules.rides.api.v1.serializers.rides import RideListSerializer
from modules.rides.models import Ride
from modules.rides.selectors.ride_selector import RideSelector
from shared.errors.exceptions import ValidationError


class RideViewSet(ReadOnlyModelViewSet):
    queryset = Ride.objects.none()
    serializer_class = RideListSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "status": ["exact"],
        "id_rider__email": ["exact", "icontains"],
    }
    ordering_fields = ["pickup_time", "distance"]
    ordering = ["-pickup_time"]

    def get_queryset(self):
        lat = self.request.query_params.get("lat")
        lng = self.request.query_params.get("lng")

        if lat is not None and lng is not None:
            lat, lng = self._validate_coordinates(lat, lng)
            return RideSelector.list_rides_by_distance(lat=lat, lng=lng)

        return RideSelector.list_rides()

    @staticmethod
    def _validate_coordinates(lat, lng):
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            raise ValidationError(
                detail="lat and lng must be valid numbers.",
                extra={"fields": {"lat": [lat], "lng": [lng]}},
            )

        if not (-90 <= lat <= 90):
            raise ValidationError(
                detail="lat must be between -90 and 90.",
                extra={"fields": {"lat": [str(lat)]}},
            )

        if not (-180 <= lng <= 180):
            raise ValidationError(
                detail="lng must be between -180 and 180.",
                extra={"fields": {"lng": [str(lng)]}},
            )

        return lat, lng
