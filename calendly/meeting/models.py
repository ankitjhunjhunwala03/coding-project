from django.db import models
from django.utils import timezone
from user.models import User
# from .utils import create_recurring_meetings


class Meeting(models.Model):
    participants = models.ManyToManyField(User, related_name="meetings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Recurrence fields (unchanged from the previous implementation)
    is_recurring = models.BooleanField(default=False)
    recurrence_type = models.CharField(
        max_length=10,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        null=True, blank=True
    )
    interval = models.PositiveIntegerField(default=1)  # Interval for recurrence, e.g., every 2 weeks
    recurrence_end_date = models.DateField(null=True, blank=True)  # Optional end date for recurrence

    def __str__(self):
        participants_list = ", ".join([user.username for user in self.participants.all()])
        return f"Meeting with {participants_list} from {self.start_time} to {self.end_time}"