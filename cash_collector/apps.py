from django.apps import AppConfig


class CashCollectorConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "cash_collector"

	def ready(self):
		pass
