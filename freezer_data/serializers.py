from rest_framework import serializers
from .models import FreezerSensorData


class FreezerSensorDataSerializer(serializers.ModelSerializer):
    # Accept the external IoT payload keys while storing normalized fields.
    DeviceId = serializers.CharField(source='device_id', required=False, write_only=True)
    device_id = serializers.CharField(required=False)
    ChipMac = serializers.CharField(source='chip_mac', required=False, write_only=True)
    chip_mac = serializers.CharField(required=False)
    Temp = serializers.FloatField(source='temperature', required=False, write_only=True)
    temperature = serializers.FloatField(required=False)
    BatPer = serializers.FloatField(source='battery_percent', required=False, write_only=True)
    battery_percent = serializers.FloatField(required=False)
    Current = serializers.FloatField(source='current', required=False, write_only=True)
    Energy = serializers.FloatField(source='energy', required=False, write_only=True)
    lng = serializers.FloatField(required=False)

    class Meta:
        model = FreezerSensorData
        fields = [
            'id',
            'DeviceId',
            'device_id',
            'ChipMac',
            'chip_mac',
            'Temp',
            'temperature',
            'BatPer',
            'battery_percent',
            'Current',
            'Energy',
            'current',
            'energy',
            'lat',
            'lng',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        attrs['device_id'] = attrs.get('device_id') or self.initial_data.get('device_id') or self.initial_data.get('DeviceId')
        attrs['chip_mac'] = attrs.get('chip_mac') or self.initial_data.get('chip_mac') or self.initial_data.get('ChipMac')
        attrs['temperature'] = attrs.get('temperature') if attrs.get('temperature') is not None else self.initial_data.get('Temp')
        attrs['battery_percent'] = attrs.get('battery_percent') if attrs.get('battery_percent') is not None else self.initial_data.get('BatPer')

        required_fields = {
            'device_id': attrs.get('device_id'),
            'chip_mac': attrs.get('chip_mac'),
            'temperature': attrs.get('temperature'),
            'battery_percent': attrs.get('battery_percent'),
            'current': attrs.get('current'),
            'energy': attrs.get('energy'),
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
            'chip_mac',
            'temperature',
            'battery_percent',
            'current',
            'energy',
            'lat',
            'lng',
            'created_at',
        ]
        read_only_fields = fields
