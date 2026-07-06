from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Freezer, FreezerSensorData
from .serializers import (
    FreezerCreateSerializer,
    FreezerSerializer,
    FreezerSensorDataResponseSerializer,
    FreezerSensorDataSerializer,
)

FREEZER_LOOKUP_PARAMS = ('device_id', 'batch_code', 'serial_number')


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


@extend_schema(
    tags=['Freezers'],
    methods=['POST'],
    summary='Register a freezer',
    request=FreezerCreateSerializer,
    responses={201: FreezerSerializer},
)
@extend_schema(
    tags=['Freezers'],
    methods=['GET'],
    summary='List all freezers or look up by identifier',
    description=(
        'With no query parameters, returns all registered freezers. '
        'With exactly one of `device_id`, `batch_code`, or `serial_number`, returns matching freezers.'
    ),
    parameters=[
        OpenApiParameter(name='device_id', type=str, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='batch_code', type=str, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='serial_number', type=str, location=OpenApiParameter.QUERY, required=False),
    ],
    responses={200: FreezerSerializer(many=True)},
)
@api_view(['GET', 'POST'])
def freezer_list_create(request):
    if request.method == 'POST':
        serializer = FreezerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        freezer = serializer.save()
        return Response(FreezerSerializer(freezer).data, status=status.HTTP_201_CREATED)

    provided = [
        (param, request.query_params.get(param))
        for param in FREEZER_LOOKUP_PARAMS
        if request.query_params.get(param) not in (None, '')
    ]

    if len(provided) > 1:
        return Response(
            {'detail': 'Provide at most one of: device_id, batch_code, serial_number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(provided) == 1:
        field_name, value = provided[0]
        freezers = Freezer.objects.filter(**{field_name: value})
        if not freezers.exists():
            return Response({'detail': 'No registered freezer found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        freezers = Freezer.objects.all()

    return Response(FreezerSerializer(freezers, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezers'],
    summary='Get a registered freezer by id',
    responses={200: FreezerSerializer},
)
@api_view(['GET'])
def get_freezer_detail(request, pk):
    freezer = get_object_or_404(Freezer, pk=pk)
    return Response(FreezerSerializer(freezer).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezers'],
    summary='Toggle freezer status',
    description='Sets status to 0 if currently 1, or to 1 if currently 0.',
    request=None,
    responses={200: FreezerSerializer},
)
@api_view(['PATCH'])
def toggle_freezer_status(request, pk):
    freezer = get_object_or_404(Freezer, pk=pk)
    freezer.status = (
        Freezer.Status.OFF if freezer.status == Freezer.Status.ON else Freezer.Status.ON
    )
    freezer.save(update_fields=['status', 'updated_at'])
    return Response(FreezerSerializer(freezer).data, status=status.HTTP_200_OK)
