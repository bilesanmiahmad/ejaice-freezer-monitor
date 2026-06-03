# Ejaice Freezer Monitor

A Django REST API for ingesting and querying freezer telemetry from IoT sensors.

## Supported Incoming Payload Keys

This API accepts IoT key names directly, or the normalized snake_case equivalents. Either form can be mixed in the same request.

```json
{
  "DeviceId": "1",
  "BatchCode": "B001",
  "SerialNumber": "SN-42",
  "ChipMac": "00:00:00:00",
  "Temp": "12",
  "BatPer": "78",
  "Current": "40.3",
  "CurrentCons": "10.1",
  "Energy": "0.03",
  "EnergyCons": "0.01",
  "NetSignal": "-65",
  "lat": "6.345601",
  "lng": "3.650123"
}
```

| IoT key | Stored field |
| --- | --- |
| `DeviceId` | `device_id` |
| `BatchCode` | `batch_code` |
| `SerialNumber` | `serial_number` |
| `ChipMac` | `chip_mac` |
| `Temp` | `temperature` |
| `BatPer` | `battery_percent` |
| `Current` | `current_generation` |
| `CurrentCons` | `current_consumption` |
| `Energy` | `energy_generation` |
| `EnergyCons` | `energy_consumption` |
| `NetSignal` | `network_signal` |
| `lat` | `lat` |
| `lng` | `lng` |

All fields above are required on `POST /api/v1/freezer-data/`.

## Authentication

All API endpoints require a valid token except `POST /api/v1/auth/token/`.

Send the token on every request:

```http
Authorization: Token <your-api-token>
```

Obtain a token with username and password:

```bash
curl -X POST http://localhost:8001/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-user", "password": "your-password"}'
```

Or create one for an existing user:

```bash
python manage.py drf_create_token your-user
```

Create a Django user first if needed:

```bash
python manage.py createsuperuser
```

## Response Format

`POST` and `GET` endpoints return normalized field names:

```json
{
  "id": 1,
  "device_id": "1",
  "batch_code": "B001",
  "serial_number": "SN-42",
  "chip_mac": "00:00:00:00",
  "temperature": 12.0,
  "battery_percent": 78.0,
  "current_generation": 40.3,
  "current_consumption": 10.1,
  "energy_generation": 0.03,
  "energy_consumption": 0.01,
  "network_signal": -65.0,
  "lat": 6.345601,
  "lng": 3.650123,
  "created_at": "2026-05-28T12:00:00Z"
}
```

## Endpoints

- `POST /api/v1/auth/token/` obtain API token (username + password)
- `POST /api/v1/freezer-data/` create new freezer telemetry row
- `GET /api/v1/freezer-data/last/` latest row globally
- `GET /api/v1/freezer-data/last/all/` latest row per freezer (`device_id`)
- `GET /api/v1/freezer-data/last/all/serial/` latest row per freezer (`serial_number`)
- `GET /api/v1/freezer-data/device/{device_id}/` latest row by device
- `GET /api/schema/` OpenAPI schema (public)
- `GET /api/docs/` Swagger UI (public; use **Authorize** to add your token for try-it-out requests)
- `GET /api/redoc/` ReDoc (public)

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
