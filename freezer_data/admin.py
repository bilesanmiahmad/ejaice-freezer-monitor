from django.contrib import admin
from .models import Freezer, FreezerSensorData


@admin.register(Freezer)
class FreezerAdmin(admin.ModelAdmin):
    list_display = ('id', 'serial_number', 'device_id', 'batch_code', 'chip_mac', 'status', 'updated_at')
    search_fields = ('serial_number', 'device_id', 'chip_mac', 'batch_code')
    list_filter = ('status', 'created_at')


@admin.register(FreezerSensorData)
class FreezerSensorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'device_id', 'serial_number', 'chip_mac', 'temperature', 'battery_percent', 'created_at')
    search_fields = ('device_id', 'serial_number', 'chip_mac')
    list_filter = ('created_at',)
