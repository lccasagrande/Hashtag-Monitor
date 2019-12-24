from django.apps import AppConfig


class MonitorConfig(AppConfig):
    name = 'hashtag_monitor.apps.monitor'

    def ready(self):
        from . import tasks
        tasks.start()
