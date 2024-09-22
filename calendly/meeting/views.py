import pytz
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta, datetime
from .models import Meeting
from .serializers import MeetingSerializer
from user.models import User
from rest_framework.response import Response
from .utils import can_schedule_meeting, can_schedule_recurring_meeting, create_recurring_meetings
from django.db.models import Q


class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.request.query_params.get('users'):
            users = self.request.query_params['users'].split(',')
            queryset = queryset.filter(participants__in=users)
        if self.request.query_params.get('start_datetime'):
            queryset = queryset.filter(start_time__gte=self.request.query_params['start_datetime'])
        if self.request.query_params.get('end_datetime'):
            queryset = queryset.filter(end_time__lte=self.request.query_params['end_datetime'])
        return queryset

    def create(self, request, *args, **kwargs):
        participants = User.objects.filter(id__in=request.data['participants'])
        start_time = pytz.timezone('UTC').localize(datetime.strptime(request.data['start_time'], '%Y-%m-%dT%H:%M:%SZ'))
        end_time = pytz.timezone('UTC').localize(datetime.strptime(request.data['end_time'], '%Y-%m-%dT%H:%M:%SZ'))
        is_recurring = request.data.get('is_recurring', False)

        if is_recurring:
            recurrence_type = request.data['recurrence_type']
            interval = request.data['interval']
            recurrence_end_date = pytz.timezone('UTC').localize(
                datetime.strptime(request.data['recurrence_end_date'], '%Y-%m-%d')).date()

            if can_schedule_recurring_meeting(participants, start_time, end_time, recurrence_type, interval,
                                              recurrence_end_date):
                meeting = Meeting.objects.create(
                    start_time=start_time,
                    end_time=end_time,
                    is_recurring=is_recurring,
                    recurrence_type=recurrence_type,
                    interval=interval,
                    recurrence_end_date=recurrence_end_date
                )
                meeting.participants.add(*participants)
                create_recurring_meetings(meeting)
                return Response({'message': 'Recurring meeting created successfully!'})
            else:
                return Response({'error': 'Users are not available for recurring meeting'}, status=400)
        else:
            if not can_schedule_meeting(participants, start_time, end_time):
                return Response({'error': 'Users are not available for meeting'})

            super(MeetingViewSet, self).create(request, *args, **kwargs)
            return Response({'message': 'Meeting created successfully!'})
