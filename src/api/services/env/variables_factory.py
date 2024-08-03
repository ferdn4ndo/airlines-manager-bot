import os

from .environment import Environment


variables = Environment()

# Hosts and ports
variables.set(key='VIRTUAL_HOST', default='api.ambot.lan', description='The hostname of the container'),
variables.set(key='LETSENCRYPT_HOST', description='The hostname of the HTTPS SSL certificate'),
variables.set(key='LETSENCRYPT_EMAIL', description='The email of the owner of the HTTPS SSL certificate'),
variables.set(key='APPLICATION_HOST', default='ambot.lan', description='The hostname of the main application'),
variables.set(key='APPLICATION_PORT', default='5000', description='The port where the service is running'),
variables.set(key='FRONTEND_URL', default='http://ambot.lan', description='The base URL of the frontend'),

# Server config
variables.set(key='ENV_MODE', default='dev', description='The environment mode to run the server: "prod" or "dev"'),
variables.set(key='GUVICORN_WORKERS', default='3', description='Number of workers to spawn when running in "prod"'),
variables.set(key='LOG_LEVEL', default="warning", description='Minimum log level to notify'),

# AM Credentials
variables.set(key='AM_USER_EMAIL', required=True, description='Username of the Airlines Manager account'),
variables.set(key='AM_USER_PASSWORD', required=True, description='Password of the Airlines Manager account'),

# Time intervals
variables.set(key='REQUEST_INTERVAL_MIN', default='1')
variables.set(key='REQUEST_INTERVAL_MAX', default='5')
variables.set(key='WAIT_TIME_MIN', default='5000')
variables.set(key='WAIT_TIME_MAX', default='10000')
variables.set(key='LINE_UPDATE_INTERVAL_DAYS', default='2')

# uServer-Auth connection params
variables.set(key='USERVER_AUTH_HOST', default='userver-auth:5000')
variables.set(key='USERVER_AUTH_SYSTEM_NAME', default='ambot')
variables.set(key='USERVER_AUTH_SYSTEM_TOKEN', default='tyPdRAAcUcFAZiiDPLmUNMJYK2rP4hBmMVVd4YadJPg')
variables.set(key='USERVER_AUTH_USER', default='ambot-root')
variables.set(key='USERVER_AUTH_PASSWORD', default='dtwsFykiL9cYTpVWqLY3vz')

# Django key
variables.set(key='DJANGO_SECRET_KEY', default='FRA8NnvJp3oCqqyg8qurro2SpqRnU6nAjkib5DPUQ2Bi2V6rMt')
variables.set(key='DJANGO_SUPERUSER_ID', default='da2f313aa0c646f49398ace13cad259f')
variables.set(key='DJANGO_SUPERUSER_PASSWORD', default='nmGSvZLa8YvHkuxq')

# DB credentials
variables.set(key='DB_ENGINE', default='sqlite', description='Database engine (either sqlite or postgres)')
variables.set(key='SQLITE_FILEPATH', default='/data/db.sqlite', required=(variables.get('DB_ENGINE') == 'sqlite'))
variables.set(key='POSTGRES_HOST', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='POSTGRES_DB', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='POSTGRES_USER', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='POSTGRES_PASS', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='POSTGRES_PORT', default='5432', required=(variables.get('DB_ENGINE') == 'postgres'))

# For setup only
variables.set(key='POSTGRES_ROOT_USER', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='POSTGRES_ROOT_PASS', required=(variables.get('DB_ENGINE') == 'postgres'))
variables.set(key='USERVER_AUTH_SYSTEM_CREATION_TOKEN', required=True)
