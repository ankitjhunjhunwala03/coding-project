import pytz
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, datetime
from .models import Meeting
from .serializers import MeetingSerializer
from user.models import User
from rest_framework.response import Response
from .utils import can_schedule_meeting


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def create(self, request, *args, **kwargs):
        user1 = User.objects.get(pk=request.data['user1'])
        user2 = User.objects.get(pk=request.data['user2'])
        start_time = pytz.timezone('UTC').localize(datetime.strptime(request.data['start_time'], '%Y-%m-%dT%H:%M:%SZ'))
        end_time = pytz.timezone('UTC').localize(datetime.strptime(request.data['end_time'], '%Y-%m-%dT%H:%M:%SZ'))
        
        if not can_schedule_meeting(user1, user2, start_time, end_time):
            return Response({'error': 'Unavailable Slot'})

        return super(MeetingViewSet, self).create(request, *args, **kwargs)
