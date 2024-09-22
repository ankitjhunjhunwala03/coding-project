from django.db import models
from django.utils import timezone
from user.models import User
from availability.models import SpecificDateAvailabilitySlot, WeeklyAvailabilitySlot


class Meeting(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_meetings')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_meetings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()