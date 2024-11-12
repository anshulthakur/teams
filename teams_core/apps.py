from django.apps import AppConfig


class TeamsCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teams_core'

    def ready(self):
        import teams_core.signals  # Import the signals module
        import teams_core.templatetags.subscription_tags