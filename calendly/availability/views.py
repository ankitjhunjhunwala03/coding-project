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
        users = request.query_params.get('users').split(',')

        start_datetime_str = request.query_params.get('start_datetime')
        end_datetime_str = request.query_params.get('end_datetime')

        start_datetime = datetime.fromisoformat(start_datetime_str)
        end_datetime = datetime.fromisoformat(end_datetime_str)

        available_slots = []
        for user in users:
            available_slots.append(get_user_availability(user, start_datetime, end_datetime))

        overlapping_slots = available_slots[0]
        for slot in  available_slots[1:]:
            overlapping_slots = break_and_find_overlapping_slots(overlapping_slots, slot)

        return Response({"available_slots": overlapping_slots})


class WeeklyAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = WeeklyAvailabilitySlot.objects.all()
    serializer_class = WeeklyAvailabilitySlotSerializer


class SpecificDateAvailabilityViewSet(viewsets.ModelViewSet):
    queryset = SpecificDateAvailabilitySlot.objects.all()
    serializer_class = SpecificDateAvailabilitySlotSerializer


class UnavailableSlotViewSet(viewsets.ModelViewSet):
    queryset = UnavailableSlot.objects.all()
    serializer_class = UnavailableSlotSerializer
