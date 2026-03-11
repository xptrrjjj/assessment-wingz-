from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.api.permissions import IsAdminRole
from modules.rides.api.v1.serializers.rides import RideListSerializer
from modules.rides.selectors.ride_selector import RideSelector


class RideViewSet(ReadOnlyModelViewSet):
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
            return RideSelector.list_rides_by_distance(
                lat=float(lat),
                lng=float(lng),
            )

        return RideSelector.list_rides()
