web: daphne hashtag_monitor.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: bin/start-pgbouncer-stunnel python scripts/manage.py runworker channel_layer -v2