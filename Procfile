web: daphne hashtag_monitor.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python scripts/manage.py runworker -v2