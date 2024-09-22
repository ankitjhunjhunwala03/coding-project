from django.db import models
from django.utils import timezone
from user.models import User


class WeeklyAvailabilitySlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[(i, str(i)) for i in range(7)])  # 0: Monday, 1: Tuesday, ... 6: Sunday
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.user.username}: {self.get_day_of_week_display()} from {self.start_time} to {self.end_time}"


class SpecificDateAvailabilitySlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}: from {self.start_time} to {self.end_time}"


class UnavailableSlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}: Unavailable from {self.start_time} to {self.end_time}"

    def save(self, *args, **kwargs):
        # Prevent overlaps with availability slots
        conflicting_slots = SpecificDateAvailabilitySlot.objects.filter(
            user=self.user,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if conflicting_slots.exists():
            raise ValueError("Unavailable slot overlaps with available slots")
        super().save(*args, **kwargs)
