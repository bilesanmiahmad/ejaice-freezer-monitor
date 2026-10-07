import csv
from io import StringIO

from django.db.models import Q
from django.utils.dateparse import parse_date

from .models import Freezer, FreezerSensorData

CSV_COLUMNS = [
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


def _sensor_match_q(freezers):
    serial_numbers = freezers.values_list('serial_number', flat=True)
    device_ids = freezers.values_list('device_id', flat=True)
    return Q(serial_number__in=serial_numbers) | Q(device_id__in=device_ids)


def parse_freezer_ids(raw_value):
    if not raw_value or not str(raw_value).strip():
        return None
    ids = []
    for part in str(raw_value).split(','):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError as exc:
            raise ValueError(f'Invalid freezer id: {part!r}') from exc
    return ids or None


def build_sensor_export_queryset(*, date=None, start_date=None, end_date=None, client_email=None, freezer_ids=None):
    queryset = FreezerSensorData.objects.all().order_by('created_at')

    if date:
        parsed = parse_date(date)
        if parsed is None:
            raise ValueError('Invalid date. Use YYYY-MM-DD.')
        queryset = queryset.filter(created_at__date=parsed)
    else:
        if start_date:
            parsed = parse_date(start_date)
            if parsed is None:
                raise ValueError('Invalid start_date. Use YYYY-MM-DD.')
            queryset = queryset.filter(created_at__date__gte=parsed)
        if end_date:
            parsed = parse_date(end_date)
            if parsed is None:
                raise ValueError('Invalid end_date. Use YYYY-MM-DD.')
            queryset = queryset.filter(created_at__date__lte=parsed)

    freezers = None
    if client_email and freezer_ids is not None:
        freezers = Freezer.objects.filter(client__email__iexact=client_email.strip(), pk__in=freezer_ids)
    elif client_email:
        freezers = Freezer.objects.filter(client__email__iexact=client_email.strip())
    elif freezer_ids is not None:
        freezers = Freezer.objects.filter(pk__in=freezer_ids)

    if freezers is not None:
        if not freezers.exists():
            return queryset.none()
        queryset = queryset.filter(_sensor_match_q(freezers))

    return queryset


def render_sensor_data_csv(queryset):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_COLUMNS)

    for row in queryset.iterator(chunk_size=500):
        writer.writerow([
            row.id,
            row.device_id,
            row.batch_code,
            row.serial_number,
            row.chip_mac,
            row.temperature,
            row.battery_percent,
            row.current_generation,
            row.current_consumption,
            row.energy_generation,
            row.energy_consumption,
            row.network_signal,
            row.lat,
            row.lng,
            row.created_at.isoformat() if row.created_at else '',
        ])

    return buffer.getvalue()
