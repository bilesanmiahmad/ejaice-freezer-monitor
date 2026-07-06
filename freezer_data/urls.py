from django.urls import path
from . import views

app_name = 'freezer_data'

urlpatterns = [
    path('freezers/', views.freezer_list_create, name='freezer_list_create'),
    path('freezers/<int:pk>/', views.get_freezer_detail, name='get_freezer_detail'),
    path('freezers/<int:pk>/toggle-status/', views.toggle_freezer_status, name='toggle_freezer_status'),
    path('freezer-data/', views.create_freezer_sensor_data, name='create_freezer_sensor_data'),
    path('freezer-data/last/', views.get_last_freezer_sensor_data, name='get_last_freezer_sensor_data'),
    path('freezer-data/last/all/', views.get_last_freezer_sensor_data_all_devices, name='get_last_freezer_sensor_data_all_devices'),
    path('freezer-data/last/all/serial/', views.get_last_freezer_sensor_data_all_serials, name='get_last_freezer_sensor_data_all_serials'),
    path('freezer-data/device/<str:device_id>/', views.get_last_freezer_sensor_data_by_device, name='get_last_freezer_sensor_data_by_device'),
]
