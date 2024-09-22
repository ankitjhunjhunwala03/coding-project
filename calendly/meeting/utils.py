import calendar
from datetime import timedelta

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


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)


def create_recurring_meetings(meeting):
    recurrence_type = meeting.recurrence_type
    interval = meeting.interval
    current_start = meeting.start_time
    current_end = meeting.end_time

    delta = timedelta(seconds=0)
    if recurrence_type == 'daily':
        delta = timedelta(days=interval)
    elif recurrence_type == 'weekly':
        delta = timedelta(weeks=interval)
    elif recurrence_type == 'monthly':
        delta = None

    while current_start.date() <= meeting.recurrence_end_date:
        if can_schedule_meeting(meeting.participants.all(), current_start, current_end):
            m = Meeting.objects.create(
                start_time=current_start,
                end_time=current_end,
                is_recurring=False
            )
            m.participants.add(*meeting.participants.all())
        if recurrence_type == 'monthly':
            current_start = add_months(current_start, interval)
            current_end = add_months(current_end, interval)
        else:
            current_start += delta
            current_end += delta


def can_schedule_recurring_meeting(participants, current_start, current_end, recurrence_type, interval,
                                   recurrence_end_date):
    delta = timedelta(seconds=0)
    if recurrence_type == 'daily':
        delta = timedelta(days=interval)
    elif recurrence_type == 'weekly':
        delta = timedelta(weeks=interval)
    elif recurrence_type == 'monthly':
        delta = None

    while current_start.date() <= recurrence_end_date:
        if not can_schedule_meeting(participants, current_start, current_end):
            return False

        if recurrence_type == 'monthly':
            current_start = add_months(current_start, interval)
            current_end = add_months(current_end, interval)
        else:
            current_start += delta
            current_end += delta

    return True
