from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from datetime import datetime
from .utils import get_user_availability, break_and_find_overlapping_slots
from user.models import User
from .models import WeeklyAvailabilitySlot, SpecificDateAvailabilitySlot, UnavailableSlot
from .serializers import WeeklyAvailabilitySlotSerializer, SpecificDateAvailabilitySlotSerializer, \
    UnavailableSlotSerializer


class AvailabilityViewSet(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.query_params.get('user_id'))

        start_datetime_str = request.query_params.get('start_datetime')
        end_datetime_str = request.query_params.get('end_datetime')

        start_datetime = datetime.fromisoformat(start_datetime_str)
        end_datetime = datetime.fromisoformat(end_datetime_str)

        available_slots = get_user_availability(user, start_datetime, end_datetime)

        return Response({"available_slots": available_slots})


class OverlappingAvailabilityViewSet(APIView):
    def get(self, request, *args, **kwargs):
        user1 = User.objects.get(pk=request.query_params.get('user_id1'))
        user2 = User.objects.get(pk=request.query_params.get('user_id2'))

        start_datetime_str = request.query_params.get('start_datetime')
        end_datetime_str = request.query_params.get('end_datetime')

        start_datetime = datetime.fromisoformat(start_datetime_str)
        end_datetime = datetime.fromisoformat(end_datetime_str)

        available_slots1 = get_user_availability(user1, start_datetime, end_datetime)
        available_slots2 = get_user_availability(user2, start_datetime, end_datetime)

        available_slots = break_and_find_overlapping_slots(available_slots1, available_slots2)

        return Response({"available_slots": available_slots})


class WeeklyAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = WeeklyAvailabilitySlot.objects.all()
    serializer_class = WeeklyAvailabilitySlotSerializer


class SpecificDateAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = SpecificDateAvailabilitySlot.objects.all()
    serializer_class = SpecificDateAvailabilitySlotSerializer


class UnavailableSlotViewSet(viewsets.ModelViewSet):
    queryset = UnavailableSlot.objects.all()
    serializer_class = UnavailableSlotSerializer
