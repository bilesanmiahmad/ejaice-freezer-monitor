# Ejaice Freezer Monitor

A Django REST API for ingesting and querying freezer telemetry from IoT sensors.

## Supported Incoming Payload Keys

This API accepts your IoT key names directly:

```json
{
  "DeviceId": "1",
  "ChipMac": "00:00:00:00",
  "Temp": "12",
  "BatPer": "78",
  "Current": "40.3",
  "Energy": "0.03",
  "lat": "6.345601",
  "lng": "3.650123"
}
```

## Endpoints

- `POST /api/v1/freezer-data/` create new freezer telemetry row
- `GET /api/v1/freezer-data/last/` latest row globally
- `GET /api/v1/freezer-data/device/{device_id}/` latest row by device
- `GET /api/docs/` Swagger UI

## Local Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

## Docker Setup

```bash
cp .env.example .env
docker-compose up --build
```
