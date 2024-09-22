from django.urls import path, include
from rest_framework import routers
from .views import MeetingViewSet

router = routers.DefaultRouter()
router.register('', MeetingViewSet, basename='meetings')

urlpatterns = [
    path('', include(router.urls)),
]
