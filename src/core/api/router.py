from rest_framework.routers import DefaultRouter

from modules.rides.api.v1.views.rides import RideViewSet

router = DefaultRouter()
router.register("rides", RideViewSet, basename="rides")
