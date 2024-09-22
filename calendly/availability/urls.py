from django.urls import path, include
from rest_framework import routers
from .views import AvailabilityViewSet, WeeklyAvailabilityViewSet, SpecificDateAvailabilityViewSet, \
    UnavailableSlotViewSet, OverlappingAvailabilityViewSet

router = routers.DefaultRouter()
router.register('weekly', WeeklyAvailabilityViewSet, basename='weekly')
router.register('specific', SpecificDateAvailabilityViewSet, basename='specific')
router.register('unavailable', UnavailableSlotViewSet, basename='unavailable')

urlpatterns = [
    path('', AvailabilityViewSet.as_view(), name='availability'),
    path('overlap/', OverlappingAvailabilityViewSet.as_view(), name='overlapping-availability'),
    path('', include(router.urls)),
]
