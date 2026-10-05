from django.db.models import Q
from rest_framework.permissions import BasePermission

from .models import Freezer, FreezerSensorData


class IsBackOfficeAdmin(BasePermission):
    """Staff users (back-office admins) who manage freezers and assignments."""

    message = 'Back-office admin access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def freezers_for_user(user):
    if user.is_staff:
        return Freezer.objects.all()
    return Freezer.objects.filter(client=user)


def sensor_data_for_user(user):
    if user.is_staff:
        return FreezerSensorData.objects.all()

    assigned = Freezer.objects.filter(client=user)
    serial_numbers = assigned.values_list('serial_number', flat=True)
    device_ids = assigned.values_list('device_id', flat=True)
    return FreezerSensorData.objects.filter(
        Q(serial_number__in=serial_numbers) | Q(device_id__in=device_ids)
    )


def user_can_access_freezer(user, freezer):
    if user.is_staff:
        return True
    return freezer.client_id == user.id


def user_can_access_sensor_row(user, row):
    if user.is_staff:
        return True
    assigned = Freezer.objects.filter(client=user)
    return assigned.filter(
        Q(serial_number=row.serial_number) | Q(device_id=row.device_id)
    ).exists()
