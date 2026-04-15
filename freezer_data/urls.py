from django.urls import path
from . import views

app_name = 'freezer_data'

urlpatterns = [
    path('freezer-data/', views.create_freezer_sensor_data, name='create_freezer_sensor_data'),
    path('freezer-data/last/', views.get_last_freezer_sensor_data, name='get_last_freezer_sensor_data'),
    path('freezer-data/device/<str:device_id>/', views.get_last_freezer_sensor_data_by_device, name='get_last_freezer_sensor_data_by_device'),
]
