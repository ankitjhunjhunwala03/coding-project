from .models import Meeting
from django.db.models import Q


def can_schedule_meeting(user1, user2, meeting_start_time, meeting_end_time):
    from availability.utils import get_user_availability, break_and_find_overlapping_slots
    user1_slots = get_user_availability(user1, meeting_start_time, meeting_end_time)
    user2_slots = get_user_availability(user2, meeting_start_time, meeting_end_time)

    overlapping_slots = break_and_find_overlapping_slots(user1_slots, user2_slots)

    for slot in overlapping_slots:
        available_start, available_end = slot
        if available_start <= meeting_start_time and available_end >= meeting_end_time:
            return True

    return False


def get_meeting_times(user, start_datetime, end_datetime):
    meetings = Meeting.objects.filter(Q(user1=user) | Q(user2=user)).filter(
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    ).values_list('start_time', 'end_time')
    return list(meetings)
