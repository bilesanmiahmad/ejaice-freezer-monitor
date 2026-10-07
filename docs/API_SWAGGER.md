# Freezer Monitor Swagger

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`

Use **Authorize** in Swagger UI with `Token <your-api-token>` to call protected endpoints.

## CSV export (Swagger tag: **Export**)

| Method | Path | Access |
| --- | --- | --- |
| `GET` | `/api/v1/freezer-data/export/` | Staff / back-office admin only |

### Query parameters (all optional)

| Parameter | Description |
| --- | --- |
| `date` | Single day `YYYY-MM-DD` (UTC date of `created_at`) |
| `start_date` | Range start (inclusive) |
| `end_date` | Range end (inclusive) |
| `client_email` | Freezers assigned to this client |
| `freezer_ids` | Comma-separated `Freezer` ids, e.g. `1,2,3` |

If no date parameters are provided, all dates are included.

### Response

- **200** — `text/csv` file download (`Content-Disposition: attachment`)
- **400** — invalid dates or `freezer_ids`
- **403** — non-admin token

### Example (curl)

```bash
curl -o export.csv \
  "http://localhost/api/v1/freezer-data/export/?start_date=2026-05-01&end_date=2026-05-31&client_email=client@example.com" \
  -H "Authorization: Token YOUR_STAFF_TOKEN"
```
