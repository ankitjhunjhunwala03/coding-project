from datetime import datetime, timedelta
import pytz
from .models import WeeklyAvailabilitySlot, SpecificDateAvailabilitySlot, UnavailableSlot
from meeting.utils import get_meeting_times

from datetime import datetime, time, timedelta


def merge_slots(slots):
    """
    Merges overlapping or adjacent time slots, considering that a day ends at 11:59 PM
    and the next day starts at 12:00 AM.

    :param slots: List of tuples (start_time, end_time) where times are datetime objects.
    :return: Merged list of tuples (start_time, end_time)
    """
    if not slots:
        return []

    # Sort slots by start time
    slots = sorted(slots, key=lambda x: x[0])

    merged_slots = [slots[0]]

    for current_start, current_end in slots[1:]:
        last_start, last_end = merged_slots[-1]

        # Handle end of day (11:59 PM) to start of next day (12:00 AM) wrapping
        if last_end.time() == time(23, 59) and current_start.time() == time(0,
                                                                            0) and last_end.date() == current_start.date():
            # Merge the slots across midnight
            merged_slots[-1] = (last_start, current_end)
        # If the current slot overlaps or touches the last one, merge them
        elif current_start <= last_end:
            merged_slots[-1] = (last_start, max(last_end, current_end))
        else:
            merged_slots.append((current_start, current_end))

    return merged_slots


def get_user_availability(user, start_datetime: datetime, end_datetime: datetime):
    available_slots = []

    # Fetch weekly availability
    weekly_slots = WeeklyAvailabilitySlot.objects.filter(user=user)

    current_datetime = start_datetime
    while current_datetime < end_datetime:
        current_day_of_week = current_datetime.weekday()  # 0 = Monday, 6 = Sunday
        day_slots = weekly_slots.filter(day_of_week=current_day_of_week)

        for slot in day_slots:
            slot_start = pytz.timezone('UTC').localize(datetime.combine(current_datetime.date(), slot.start_time))
            slot_end = pytz.timezone('UTC').localize(datetime.combine(current_datetime.date(), slot.end_time))

            if slot_end <= slot_start:
                slot_end += timedelta(days=1)  # Handle slots that span midnight

            if slot_start < end_datetime and slot_end > start_datetime:
                available_slots.append((max(slot_start, start_datetime), min(slot_end, end_datetime)))

        current_datetime += timedelta(days=1)

    # Fetch specific slot availability
    specific_slots = SpecificDateAvailabilitySlot.objects.filter(
        user=user,
        date__gte=start_datetime.date(),
        date__lte=end_datetime.date()
    )

    for slot in specific_slots:
        slot_start = pytz.timezone('UTC').localize(datetime.combine(slot.date, slot.start_time))
        slot_end = pytz.timezone('UTC').localize(datetime.combine(slot.date, slot.end_time))

        if slot_start < end_datetime and slot_end > start_datetime:
            available_slots.append((max(slot_start, start_datetime), min(slot_end, end_datetime)))

    # Fetch unavailable slots and exclude from available times
    unavailable_slots = UnavailableSlot.objects.filter(
        user=user,
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    ).values_list('start_time', 'end_time')

    meeting_slots = get_meeting_times(user, start_datetime, end_datetime)

    unavailable_slots = merge_slots(list(unavailable_slots) + meeting_slots)

    available_slots = merge_slots(available_slots)

    available_slots = subtract_meeting_slots(available_slots, unavailable_slots)

    return available_slots


def subtract_meeting_slots(availability_slots, meeting_slots):
    adjusted_availability = []

    for avail_slot in availability_slots:
        available_start = avail_slot[0]
        available_end = avail_slot[1]

        for meeting in meeting_slots:
            meeting_start = meeting[0]
            meeting_end = meeting[1]

            # If the meeting is entirely outside the availability slot, no changes are needed
            if meeting_end <= available_start or meeting_start >= available_end:
                continue

            # If the meeting overlaps, adjust availability
            if meeting_start <= available_start and meeting_end >= available_end:
                # Entire availability slot is covered by the meeting - remove it
                available_start, available_end = None, None
                break

            if meeting_start > available_start and meeting_end < available_end:
                # Meeting is in the middle of the slot - split into two slots
                adjusted_availability.append(
                    (available_start, meeting_start)
                )
                available_start = meeting_end

            elif meeting_start <= available_start < meeting_end < available_end:
                # Meeting overlaps the beginning of the availability slot
                available_start = meeting_end

            elif available_start < meeting_start <= available_end < meeting_end:
                # Meeting overlaps the end of the availability slot
                available_end = meeting_start

        if available_start and available_end and available_start < available_end:
            adjusted_availability.append((available_start, available_end))

    return adjusted_availability


def break_and_find_overlapping_slots(user1_slots, user2_slots):
    overlapping_slots = []

    i, j = 0, 0

    while i < len(user1_slots) and j < len(user2_slots):
        slot1 = user1_slots[i]
        slot2 = user2_slots[j]

        # Determine the overlap between the two slots
        start_overlap = max(slot1[0], slot2[0])
        end_overlap = min(slot1[1], slot2[1])

        # If the slots overlap, calculate the overlapping slot and append it
        if start_overlap < end_overlap:
            overlapping_slots.append((start_overlap, end_overlap))

        # Break the slot if one slot partially overlaps with another
        if slot1[1] > slot2[1]:
            j += 1
        elif slot1[1] < slot2[1]:
            i += 1
        else:
            # Move to the next slot when both slots end simultaneously
            i += 1
            j += 1

    return overlapping_slots
