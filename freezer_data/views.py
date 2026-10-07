import json
import logging

from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .csv_export import build_sensor_export_queryset, parse_freezer_ids, render_sensor_data_csv
from .openapi import (
    CSV_EXPORT_DESCRIPTION,
    CSV_EXPORT_QUERY_PARAMETERS,
    CSV_EXPORT_RESPONSES,
)
from .models import Freezer, FreezerSensorData
from .permissions import (
    IsBackOfficeAdmin,
    freezers_for_user,
    sensor_data_for_user,
)
from .serializers import (
    FreezerAssignSerializer,
    FreezerCreateSerializer,
    FreezerSerializer,
    FreezerSensorDataResponseSerializer,
    FreezerSensorDataSerializer,
)

FREEZER_LOOKUP_PARAMS = ('device_id', 'batch_code', 'serial_number')

logger = logging.getLogger(__name__)


def _log_request_body(action, request):
    try:
        body = json.dumps(request.data, default=str)
    except TypeError:
        body = str(request.data)
    logger.info('%s request body: %s', action, body)


def _latest_records_per_field(field_name, queryset):
    latest_pk = queryset.filter(
        **{field_name: OuterRef(field_name)},
    ).order_by('-created_at').values('pk')[:1]

    latest_pks = (
        queryset
        .values(field_name)
        .distinct()
        .annotate(latest_pk=Subquery(latest_pk))
        .values_list('latest_pk', flat=True)
    )

    return queryset.filter(pk__in=latest_pks).order_by('-created_at')


@extend_schema(
    tags=['Freezer data'],
    summary='Ingest freezer telemetry',
    request=FreezerSensorDataSerializer,
    responses={201: FreezerSensorDataResponseSerializer},
)
@api_view(['POST'])
@permission_classes([IsBackOfficeAdmin])
def create_freezer_sensor_data(request):
    _log_request_body('Freezer sensor ingest', request)
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
    queryset = sensor_data_for_user(request.user)
    last_record = queryset.order_by('-created_at').first()
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
    queryset = sensor_data_for_user(request.user)
    records = _latest_records_per_field('device_id', queryset)
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
    queryset = sensor_data_for_user(request.user)
    records = _latest_records_per_field('serial_number', queryset)
    serializer = FreezerSensorDataResponseSerializer(records, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry by device id',
    responses={200: FreezerSensorDataResponseSerializer},
)
@api_view(['GET'])
def get_last_freezer_sensor_data_by_device(request, device_id):
    queryset = sensor_data_for_user(request.user)
    last_record = queryset.filter(device_id=device_id).order_by('-created_at').first()
    if not last_record:
        return Response({'detail': 'No freezer sensor records found for this device.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FreezerSensorDataResponseSerializer(last_record).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Export'],
    summary='Export telemetry as CSV',
    description=CSV_EXPORT_DESCRIPTION,
    parameters=CSV_EXPORT_QUERY_PARAMETERS,
    responses=CSV_EXPORT_RESPONSES,
)
@api_view(['GET'])
@permission_classes([IsBackOfficeAdmin])
def export_freezer_sensor_data_csv(request):
    try:
        freezer_ids = parse_freezer_ids(request.query_params.get('freezer_ids'))
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        queryset = build_sensor_export_queryset(
            date=request.query_params.get('date'),
            start_date=request.query_params.get('start_date'),
            end_date=request.query_params.get('end_date'),
            client_email=request.query_params.get('client_email'),
            freezer_ids=freezer_ids,
        )
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    csv_body = render_sensor_data_csv(queryset)
    filename = f'freezer_sensor_data_{now().strftime("%Y%m%d_%H%M%S")}.csv'
    response = HttpResponse(csv_body, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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
    summary='List freezers or look up by identifier',
    description=(
        'Clients see only freezers assigned to them. Admins see all freezers. '
        'Optional query: exactly one of `device_id`, `batch_code`, or `serial_number`.'
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
        if not IsBackOfficeAdmin().has_permission(request, None):
            return Response({'detail': IsBackOfficeAdmin.message}, status=status.HTTP_403_FORBIDDEN)
        _log_request_body('Freezer registration', request)
        serializer = FreezerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        freezer = serializer.save()
        return Response(FreezerSerializer(freezer).data, status=status.HTTP_201_CREATED)

    freezers = freezers_for_user(request.user)
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
        freezers = freezers.filter(**{field_name: value})
        if not freezers.exists():
            return Response({'detail': 'No registered freezer found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(FreezerSerializer(freezers, many=True).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezers'],
    summary='Get a registered freezer by id',
    responses={200: FreezerSerializer},
)
@api_view(['GET'])
def get_freezer_detail(request, pk):
    freezer = get_object_or_404(freezers_for_user(request.user), pk=pk)
    return Response(FreezerSerializer(freezer).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezers'],
    summary='Toggle freezer status',
    description='Sets status to 0 if currently 1, or to 1 if currently 0. Admin only.',
    request=None,
    responses={200: FreezerSerializer},
)
@api_view(['PATCH'])
@permission_classes([IsBackOfficeAdmin])
def toggle_freezer_status(request, pk):
    freezer = get_object_or_404(Freezer, pk=pk)
    freezer.status = (
        Freezer.Status.OFF if freezer.status == Freezer.Status.ON else Freezer.Status.ON
    )
    freezer.save(update_fields=['status', 'updated_at'])
    return Response(FreezerSerializer(freezer).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezers'],
    summary='Assign freezer to a client user',
    description='Admin only. Pass `client_user_id` to assign, or null to unassign.',
    request=FreezerAssignSerializer,
    responses={200: FreezerSerializer},
)
@api_view(['PATCH'])
@permission_classes([IsBackOfficeAdmin])
def assign_freezer_client(request, pk):
    freezer = get_object_or_404(Freezer, pk=pk)
    serializer = FreezerAssignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    client_user_id = serializer.validated_data.get('client_user_id')

    if client_user_id is None:
        freezer.client = None
    else:
        User = get_user_model()
        freezer.client = get_object_or_404(User, pk=client_user_id, is_staff=False)

    freezer.save(update_fields=['client', 'updated_at'])
    return Response(FreezerSerializer(freezer).data, status=status.HTTP_200_OK)
