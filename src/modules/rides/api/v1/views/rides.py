from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.api.permissions import IsAdminRole
from modules.rides.api.v1.serializers.rides import RideListSerializer
from modules.rides.selectors.ride_selector import RideSelector


class RideViewSet(ReadOnlyModelViewSet):
    serializer_class = RideListSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        return RideSelector.list_rides()
