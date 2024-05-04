from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Transaction


@receiver(post_save, sender=Transaction)
def check_threshold(sender, instance, **kwargs):
	collector = instance.collector
	if Transaction.is_threshold_exceeded(collector):
		collector.is_frozen = True
		collector.save()
	else:
		collector.is_frozen = False
		collector.save()
