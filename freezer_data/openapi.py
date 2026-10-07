from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

from .csv_export import CSV_COLUMNS

CSV_EXPORT_QUERY_PARAMETERS = [
    OpenApiParameter(
        name='date',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        description=(
            'Return rows whose `created_at` falls on this calendar day (UTC). '
            'Format: `YYYY-MM-DD`. Ignores `start_date` / `end_date` when set.'
        ),
        examples=[OpenApiExample('Single day', value='2026-05-28')],
    ),
    OpenApiParameter(
        name='start_date',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        description='Inclusive start date (`YYYY-MM-DD`). Omit both dates to export all history.',
        examples=[OpenApiExample('Range start', value='2026-05-01')],
    ),
    OpenApiParameter(
        name='end_date',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        description='Inclusive end date (`YYYY-MM-DD`).',
        examples=[OpenApiExample('Range end', value='2026-05-31')],
    ),
    OpenApiParameter(
        name='client_email',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        description='Only telemetry for freezers assigned to this client user email (case-insensitive).',
        examples=[OpenApiExample('Client filter', value='client@example.com')],
    ),
    OpenApiParameter(
        name='freezer_ids',
        type=str,
        location=OpenApiParameter.QUERY,
        required=False,
        description='Comma-separated registered `Freezer` primary keys, e.g. `1,3,5`.',
        examples=[OpenApiExample('Freezer ids', value='1,2')],
    ),
]

CSV_EXPORT_RESPONSES = {
    200: OpenApiResponse(
        response=OpenApiTypes.BINARY,
        description=(
            'CSV file download (`Content-Type: text/csv`, `Content-Disposition: attachment`). '
            f'Columns: {", ".join(CSV_COLUMNS)}.'
        ),
    ),
    400: OpenApiResponse(description='Invalid `date` / `start_date` / `end_date` or malformed `freezer_ids`.'),
    403: OpenApiResponse(description='Back-office admin access required (`is_staff` user token).'),
}

CSV_EXPORT_DESCRIPTION = (
    '**Admin only** — export `FreezerSensorData` rows as CSV.\n\n'
    '- No date query params → all dates (subject to other filters).\n'
    '- `client_email` → rows for freezers assigned to that client.\n'
    '- `freezer_ids` → rows for those registered freezers (matched by `serial_number` or `device_id`).\n'
    '- `client_email` and `freezer_ids` together → intersection of both filters.'
)
