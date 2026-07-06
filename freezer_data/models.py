from django.db import models


class Freezer(models.Model):
    class Status(models.IntegerChoices):
        OFF = 0, 'Off'
        ON = 1, 'On'

    device_id = models.CharField(max_length=100)
    batch_code = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    chip_mac = models.CharField(max_length=32)
    status = models.IntegerField(choices=Status.choices, default=Status.ON)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['serial_number']
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        state = 'on' if self.status == self.Status.ON else 'off'
        return f"Freezer {self.serial_number} ({state})"


class FreezerSensorData(models.Model):
    device_id = models.CharField(max_length=100)
    batch_code = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    chip_mac = models.CharField(max_length=32)
    temperature = models.FloatField()
    battery_percent = models.FloatField()
    current_generation = models.FloatField()
    current_consumption = models.FloatField()
    energy_generation = models.FloatField()
    energy_consumption = models.FloatField()
    network_signal = models.FloatField()
    lat = models.FloatField()
    lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device_id', '-created_at']),
            models.Index(fields=['chip_mac', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"FreezerSensorData {self.serial_number} @ {self.created_at}"
    

