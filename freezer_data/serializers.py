from rest_framework import serializers
from .models import FreezerSensorData


class FreezerSensorDataSerializer(serializers.ModelSerializer):
    # Accept the external IoT payload keys while storing normalized fields.
    DeviceId = serializers.CharField(source='device_id', required=False, write_only=True)
    device_id = serializers.CharField(required=False)
    BatchCode = serializers.CharField(source='batch_code', required=False, write_only=True)
    batch_code = serializers.CharField(required=False)
    SerialNumber = serializers.CharField(source='serial_number', required=False, write_only=True)
    serial_number = serializers.CharField(required=False)
    ChipMac = serializers.CharField(source='chip_mac', required=False, write_only=True)
    chip_mac = serializers.CharField(required=False)
    Temp = serializers.FloatField(source='temperature', required=False, write_only=True)
    temperature = serializers.FloatField(required=False)
    BatPer = serializers.FloatField(source='battery_percent', required=False, write_only=True)
    battery_percent = serializers.FloatField(required=False)
    Current = serializers.FloatField(source='current_generation', required=False, write_only=True)
    current_generation = serializers.FloatField(required=False)
    CurrentCons = serializers.FloatField(source='current_consumption', required=False, write_only=True)
    current_consumption = serializers.FloatField(required=False)
    Energy = serializers.FloatField(source='energy_generation', required=False, write_only=True)
    energy_generation = serializers.FloatField(required=False)
    EnergyCons = serializers.FloatField(source='energy_consumption', required=False, write_only=True)
    energy_consumption = serializers.FloatField(required=False)
    NetSignal = serializers.FloatField(source='network_signal', required=False, write_only=True)
    network_signal = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)

    class Meta:
        model = FreezerSensorData
        fields = [
            'id',
            'DeviceId',
            'device_id',
            'BatchCode',
            'batch_code',
            'SerialNumber',
            'serial_number',
            'ChipMac',
            'chip_mac',
            'Temp',
            'temperature',
            'BatPer',
            'battery_percent',
            'Current',
            'current_generation',
            'CurrentCons',
            'current_consumption',
            'Energy',
            'energy_generation',
            'EnergyCons',
            'energy_consumption',
            'NetSignal',
            'network_signal',
            'lat',
            'lng',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def _first_present(self, *keys):
        for key in keys:
            if key in self.initial_data and self.initial_data[key] not in (None, ''):
                return self.initial_data[key]
        return None

    def validate(self, attrs):
        attrs['device_id'] = attrs.get('device_id') or self._first_present('device_id', 'DeviceId')
        attrs['batch_code'] = attrs.get('batch_code') or self._first_present('batch_code', 'BatchCode')
        attrs['serial_number'] = attrs.get('serial_number') or self._first_present('serial_number', 'SerialNumber')
        attrs['chip_mac'] = attrs.get('chip_mac') or self._first_present('chip_mac', 'ChipMac')
        attrs['temperature'] = (
            attrs['temperature'] if attrs.get('temperature') is not None else self._first_present('temperature', 'Temp')
        )
        attrs['battery_percent'] = (
            attrs['battery_percent']
            if attrs.get('battery_percent') is not None
            else self._first_present('battery_percent', 'BatPer')
        )
        attrs['current_generation'] = (
            attrs['current_generation']
            if attrs.get('current_generation') is not None
            else self._first_present('current_generation', 'Current')
        )
        attrs['current_consumption'] = (
            attrs['current_consumption']
            if attrs.get('current_consumption') is not None
            else self._first_present('current_consumption', 'CurrentCons')
        )
        attrs['energy_generation'] = (
            attrs['energy_generation']
            if attrs.get('energy_generation') is not None
            else self._first_present('energy_generation', 'Energy')
        )
        attrs['energy_consumption'] = (
            attrs['energy_consumption']
            if attrs.get('energy_consumption') is not None
            else self._first_present('energy_consumption', 'EnergyCons')
        )
        attrs['network_signal'] = (
            attrs['network_signal']
            if attrs.get('network_signal') is not None
            else self._first_present('network_signal', 'NetSignal')
        )

        required_fields = {
            'device_id': attrs.get('device_id'),
            'batch_code': attrs.get('batch_code'),
            'serial_number': attrs.get('serial_number'),
            'chip_mac': attrs.get('chip_mac'),
            'temperature': attrs.get('temperature'),
            'battery_percent': attrs.get('battery_percent'),
            'current_generation': attrs.get('current_generation'),
            'current_consumption': attrs.get('current_consumption'),
            'energy_generation': attrs.get('energy_generation'),
            'energy_consumption': attrs.get('energy_consumption'),
            'network_signal': attrs.get('network_signal'),
            'lat': attrs.get('lat'),
            'lng': attrs.get('lng'),
        }

        missing = [name for name, value in required_fields.items() if value in (None, '')]
        if missing:
            raise serializers.ValidationError({
                'detail': f"Missing required fields: {', '.join(missing)}"
            })
        return attrs


class FreezerSensorDataResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreezerSensorData
        fields = [
            'id',
            'device_id',
            'batch_code',
            'serial_number',
            'chip_mac',
            'temperature',
            'battery_percent',
            'current_generation',
            'current_consumption',
            'energy_generation',
            'energy_consumption',
            'network_signal',
            'lat',
            'lng',
            'created_at',
        ]
        read_only_fields = fields
