from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from .models import Meeting
from .serializers import MeetingSerializer
from user.models import User
from rest_framework.response import Response
from .helpers import find_available_slots


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    # permission_classes = [IsAuthenticated]

    def available_slots(self, request, user1_id, user2_id, date_str, duration):
        user1 = User.objects.get(pk=user1_id)
        user2 = User.objects.get(pk=user2_id)
        duration = timedelta(minutes=int(duration))
        date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

        available_slots = find_available_slots(user1, user2, duration, date)

        return Response({'available_slots': available_slots})
