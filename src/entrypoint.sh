#!/bin/bash

echo "-=-=- Airlines Manager Bot -=-=-"

if PGPASSWORD=${POSTGRES_ROOT_PASS} psql -h "${POSTGRES_HOST}" -U "${POSTGRES_ROOT_USER}" -p "${POSTGRES_PORT}" -lqt | cut -d \| -f 1 | grep -qw "${POSTGRES_DB}"; then
    echo "Database checking passed successfully"
else
    echo "The database checking failed to find the database '${POSTGRES_DB}'. Running setup script..."
    ./setup.sh
fi

if [ "${ENV_MODE}" == "prod" ]
then
  echo "Starting in production mode..."

  gunicorn --worker-tmp-dir /dev/shm --workers ${GUVICORN_WORKERS} --bind 0.0.0.0:${APPLICATION_PORT} api.wsgi
else
  echo "Starting in development mode..."

  #tail -f /dev/null

  python manage.py runserver 0.0.0.0:${APPLICATION_PORT}
fi
