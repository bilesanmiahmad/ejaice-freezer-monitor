from django.contrib import admin
from .models import FreezerSensorData


@admin.register(FreezerSensorData)
class FreezerSensorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_id', 'chip_mac', 'temperature', 'battery_percent', 'created_at')
    search_fields = ('device_id', 'chip_mac')
    list_filter = ('created_at',)
