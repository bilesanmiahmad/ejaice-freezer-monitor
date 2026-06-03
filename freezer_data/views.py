from django.db.models import OuterRef, Subquery
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import FreezerSensorData
from .serializers import FreezerSensorDataResponseSerializer, FreezerSensorDataSerializer


def _latest_records_per_field(field_name):
    latest_pk = FreezerSensorData.objects.filter(
        **{field_name: OuterRef(field_name)},
    ).order_by('-created_at').values('pk')[:1]

    latest_pks = (
        FreezerSensorData.objects
        .values(field_name)
        .distinct()
        .annotate(latest_pk=Subquery(latest_pk))
        .values_list('latest_pk', flat=True)
    )

    return FreezerSensorData.objects.filter(pk__in=latest_pks).order_by('-created_at')


@extend_schema(
    tags=['Freezer data'],
    summary='Ingest freezer telemetry',
    request=FreezerSensorDataSerializer,
    responses={201: FreezerSensorDataResponseSerializer},
)
@api_view(['POST'])
def create_freezer_sensor_data(request):
    serializer = FreezerSensorDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    return Response(FreezerSensorDataResponseSerializer(instance).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry globally',
    responses={200: FreezerSensorDataResponseSerializer},
)
@api_view(['GET'])
def get_last_freezer_sensor_data(request):
    last_record = FreezerSensorData.objects.order_by('-created_at').first()
    if not last_record:
        return Response({'detail': 'No freezer sensor records found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FreezerSensorDataResponseSerializer(last_record).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry for every freezer by device id',
    description='Returns the most recent record per device_id (one row per freezer).',
    responses={200: FreezerSensorDataResponseSerializer(many=True)},
)
@api_view(['GET'])
def get_last_freezer_sensor_data_all_devices(request):
    records = _latest_records_per_field('device_id')
    serializer = FreezerSensorDataResponseSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry for every freezer by serial number',
    description='Returns the most recent record per serial_number (one row per freezer).',
    responses={200: FreezerSensorDataResponseSerializer(many=True)},
)
@api_view(['GET'])
def get_last_freezer_sensor_data_all_serials(request):
    records = _latest_records_per_field('serial_number')
    serializer = FreezerSensorDataResponseSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry by device id',
    responses={200: FreezerSensorDataResponseSerializer},
)
@api_view(['GET'])
def get_last_freezer_sensor_data_by_device(request, device_id):
    last_record = FreezerSensorData.objects.filter(device_id=device_id).order_by('-created_at').first()
    if not last_record:
        return Response({'detail': 'No freezer sensor records found for this device.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FreezerSensorDataResponseSerializer(last_record).data, status=status.HTTP_200_OK)
