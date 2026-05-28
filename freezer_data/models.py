from django.db import models


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
