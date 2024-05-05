# Generated by Django 5.0.4 on 2024-05-05 10:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("cash_collector", "0007_user_manager_alter_transaction_task"),
	]

	operations = [
		migrations.RemoveField(
			model_name="transaction",
			name="deleted",
		),
		migrations.RemoveField(
			model_name="transaction",
			name="manager",
		),
		migrations.AlterField(
			model_name="transaction",
			name="task",
			field=models.ForeignKey(
				on_delete=django.db.models.deletion.CASCADE,
				related_name="transactions",
				to="cash_collector.task",
			),
		),
	]