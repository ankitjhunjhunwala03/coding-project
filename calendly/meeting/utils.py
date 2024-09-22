from .models import Meeting


def can_schedule_meeting(participants, meeting_start_time, meeting_end_time):
    from availability.utils import get_user_availability, break_and_find_overlapping_slots

    overlapping_slots = get_user_availability(participants[0], meeting_start_time, meeting_end_time)
    for user in participants[1:]:
        user_slot = get_user_availability(user, meeting_start_time, meeting_end_time)
        overlapping_slots = break_and_find_overlapping_slots(overlapping_slots, user_slot)

    for slot in overlapping_slots:
        available_start, available_end = slot
        if available_start <= meeting_start_time and available_end >= meeting_end_time:
            return True

    return False


def get_meeting_times(user, start_datetime, end_datetime):
    meetings = Meeting.objects.filter(participants=user).filter(
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    ).values_list('start_time', 'end_time')
    return list(meetings)
