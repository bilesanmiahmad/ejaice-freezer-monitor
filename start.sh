#!/bin/sh
set -e

echo "Waiting for database..."
for i in 1 2 3 4 5 6 7 8 9 10; do
    if python -c "import psycopg; psycopg.connect(host='${DB_HOST:-db}', dbname='${DB_NAME:-ejaice_freezer_monitor}', user='${DB_USER:-postgres}', password='${DB_PASSWORD:-postgres}')" 2>/dev/null; then
        echo "Database is ready!"
        break
    fi
    echo "Database not ready yet... retrying ($i/10)"
    sleep 2
done

DB_NAME_CHECK="${DB_NAME:-ejaice_freezer_monitor}"
DB_HOST_CHECK="${DB_HOST:-db}"
DB_USER_CHECK="${DB_USER:-postgres}"
DB_PORT_CHECK="${DB_PORT:-5432}"
DB_PASS_CHECK="${DB_PASSWORD:-postgres}"

export PGPASSWORD="$DB_PASS_CHECK"
if ! psql -h "$DB_HOST_CHECK" -U "$DB_USER_CHECK" -p "$DB_PORT_CHECK" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME_CHECK}'" | grep -q 1; then
    echo "Database '$DB_NAME_CHECK' not found. Creating..."
    psql -h "$DB_HOST_CHECK" -U "$DB_USER_CHECK" -p "$DB_PORT_CHECK" -d postgres -c "CREATE DATABASE \"${DB_NAME_CHECK}\";"
else
    echo "Database '$DB_NAME_CHECK' already exists."
fi
unset PGPASSWORD

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser \
        --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

: "${PORT:=8000}"

if [ "${SERVER:-uvicorn}" = "gunicorn" ]; then
    exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers ${GUNICORN_WORKERS:-1}
else
    exec uvicorn config.asgi:application --host 0.0.0.0 --port $PORT --workers ${GUNICORN_WORKERS:-1} --limit-concurrency ${UVICORN_LIMIT_CONCURRENCY:-30} --lifespan off
fi
