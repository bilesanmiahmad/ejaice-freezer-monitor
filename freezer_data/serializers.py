from rest_framework import serializers
from .models import Freezer, FreezerSensorData


class FreezerSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Freezer
        fields = [
            'id',
            'device_id',
            'batch_code',
            'serial_number',
            'chip_mac',
            'status',
            'status_label',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class FreezerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Freezer
        fields = ['device_id', 'batch_code', 'serial_number', 'chip_mac', 'status']

    def validate_status(self, value):
        if value not in (Freezer.Status.OFF, Freezer.Status.ON):
            raise serializers.ValidationError('Status must be 0 (off) or 1 (on).')
        return value


class FreezerSensorDataSerializer(serializers.ModelSerializer):
    # Accept all payload values as strings (IoT devices often send string values).
    DeviceId = serializers.CharField(source='device_id', required=False, write_only=True)
    device_id = serializers.CharField(required=False)
    BatchCode = serializers.CharField(source='batch_code', required=False, write_only=True)
    batch_code = serializers.CharField(required=False)
    SerialNumber = serializers.CharField(source='serial_number', required=False, write_only=True)
    serial_number = serializers.CharField(required=False)
    ChipMac = serializers.CharField(source='chip_mac', required=False, write_only=True)
    chip_mac = serializers.CharField(required=False)
    Temp = serializers.CharField(source='temperature', required=False, write_only=True)
    temperature = serializers.CharField(required=False)
    BatPer = serializers.CharField(source='battery_percent', required=False, write_only=True)
    battery_percent = serializers.CharField(required=False)
    Current = serializers.CharField(source='current_generation', required=False, write_only=True)
    current_generation = serializers.CharField(required=False)
    CurrentCons = serializers.CharField(source='current_consumption', required=False, write_only=True)
    current_consumption = serializers.CharField(required=False)
    Energy = serializers.CharField(source='energy_generation', required=False, write_only=True)
    energy_generation = serializers.CharField(required=False)
    EnergyCons = serializers.CharField(source='energy_consumption', required=False, write_only=True)
    energy_consumption = serializers.CharField(required=False)
    NetSignal = serializers.CharField(source='network_signal', required=False, write_only=True)
    network_signal = serializers.CharField(required=False)
    lat = serializers.CharField(required=False)
    lng = serializers.CharField(required=False)

    FIELD_ALIASES = {
        'device_id': ('device_id', 'DeviceId'),
        'batch_code': ('batch_code', 'BatchCode'),
        'serial_number': ('serial_number', 'SerialNumber'),
        'chip_mac': ('chip_mac', 'ChipMac'),
        'temperature': ('temperature', 'Temp'),
        'battery_percent': ('battery_percent', 'BatPer'),
        'current_generation': ('current_generation', 'Current'),
        'current_consumption': ('current_consumption', 'CurrentCons'),
        'energy_generation': ('energy_generation', 'Energy'),
        'energy_consumption': ('energy_consumption', 'EnergyCons'),
        'network_signal': ('network_signal', 'NetSignal'),
        'lat': ('lat',),
        'lng': ('lng',),
    }

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

    def _resolve_raw(self, attrs, field_name, *alias_keys):
        value = attrs.get(field_name)
        if value not in (None, ''):
            return value
        return self._first_present(*alias_keys)

    @staticmethod
    def _coerce_str(value, field_name):
        if value is None or value == '':
            return None
        return str(value).strip()

    def _coerce_float(self, value, field_name):
        if value is None or value == '':
            return None
        if isinstance(value, bool):
            raise serializers.ValidationError({field_name: 'A valid number is required.'})
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).strip())
        except (TypeError, ValueError) as exc:
            raise serializers.ValidationError({field_name: 'A valid number is required.'}) from exc

    def validate(self, attrs):
        errors = {}
        coerced = {}

        for field_name, alias_keys in self.FIELD_ALIASES.items():
            raw = self._resolve_raw(attrs, field_name, *alias_keys)
            try:
                if field_name in ('device_id', 'batch_code', 'serial_number', 'chip_mac'):
                    coerced[field_name] = self._coerce_str(raw, field_name)
                else:
                    coerced[field_name] = self._coerce_float(raw, field_name)
            except serializers.ValidationError as exc:
                errors.update(exc.detail)

        if errors:
            raise serializers.ValidationError(errors)

        missing = [name for name, value in coerced.items() if value in (None, '')]
        if missing:
            raise serializers.ValidationError({
                'detail': f"Missing required fields: {', '.join(missing)}"
            })

        return coerced


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
