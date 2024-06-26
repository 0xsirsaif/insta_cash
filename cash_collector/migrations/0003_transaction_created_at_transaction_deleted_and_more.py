# Generated by Django 5.0.4 on 2024-05-04 16:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("cash_collector", "0002_alter_customer_address_alter_customer_email_and_more"),
	]

	operations = [
		migrations.AddField(
			model_name="transaction",
			name="created_at",
			field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
			preserve_default=False,
		),
		migrations.AddField(
			model_name="transaction",
			name="deleted",
			field=models.BooleanField(default=False),
		),
		migrations.AddField(
			model_name="transaction",
			name="updated_at",
			field=models.DateTimeField(auto_now=True),
		),
	]
