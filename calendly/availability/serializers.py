from rest_framework import serializers
from .models import WeeklyAvailabilitySlot, SpecificDateAvailabilitySlot, UnavailableSlot


class WeeklyAvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyAvailabilitySlot
        fields = '__all__'


class SpecificDateAvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificDateAvailabilitySlot
        fields = '__all__'


class UnavailableSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnavailableSlot
        fields = '__all__'
