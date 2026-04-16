from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import FreezerSensorData
from .serializers import FreezerSensorDataResponseSerializer, FreezerSensorDataSerializer


@extend_schema(
    tags=['Freezer data'],
    summary='Ingest freezer telemetry',
    request=FreezerSensorDataSerializer,
    responses={201: FreezerSensorDataResponseSerializer},
)
@api_view(['POST'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def get_last_freezer_sensor_data(request):
    last_record = FreezerSensorData.objects.order_by('-created_at').first()
    if not last_record:
        return Response({'detail': 'No freezer sensor records found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FreezerSensorDataResponseSerializer(last_record).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Freezer data'],
    summary='Get latest telemetry by device id',
    responses={200: FreezerSensorDataResponseSerializer},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_last_freezer_sensor_data_by_device(request, device_id):
    last_record = FreezerSensorData.objects.filter(device_id=device_id).order_by('-created_at').first()
    if not last_record:
        return Response({'detail': 'No freezer sensor records found for this device.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(FreezerSensorDataResponseSerializer(last_record).data, status=status.HTTP_200_OK)
