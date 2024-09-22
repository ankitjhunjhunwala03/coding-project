from .models import Meeting
from datetime import datetime
from django.db.models import Q


def get_meeting_times(user, start_datetime: datetime, end_datetime: datetime):
    meetings = Meeting.objects.filter(Q(user1=user) | Q(user2=user)).filter(
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    ).values_list('start_time', 'end_time')

    return list(meetings)
