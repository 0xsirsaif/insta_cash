from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
	is_manager = models.BooleanField(default=False)
	manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
	is_frozen = models.BooleanField(default=False)
	auth_token = models.CharField(max_length=100, blank=True, null=True)
	# Add related_name arguments to the groups and user_permissions fields
	groups = models.ManyToManyField(
		"auth.Group",
		blank=True,
		related_name="cash_collector_user_set",
		related_query_name="user",
		verbose_name=_("groups"),
	)
	user_permissions = models.ManyToManyField(
		"auth.Permission",
		blank=True,
		related_name="cash_collector_user_set",
		related_query_name="user",
		verbose_name=_("user permissions"),
	)

	def clean(self):
		super().clean()

		# Add custom validation for manager field
		if self.is_manager and self.manager is not None:
			raise ValidationError({"manager": _("A manager cannot have a manager.")})

	def __str__(self):
		return self.username


class Customer(models.Model):
	name = models.CharField(max_length=100)
	address = models.TextField(blank=True)
	phone = models.CharField(max_length=15, blank=True)
	email = models.EmailField(blank=True)

	def __str__(self):
		return self.name


class Task(models.Model):
	manager = models.ForeignKey(User, related_name="tasks_created", on_delete=models.CASCADE)
	collector = models.ForeignKey(User, related_name="tasks", on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, related_name="tasks", on_delete=models.CASCADE)

	amount_due = models.DecimalField(max_digits=10, decimal_places=2)
	amount_due_at = models.DateTimeField()
	is_collected = models.BooleanField(default=False)

	def remaining_amount(self):
		if self.is_collected:
			return 0
		total_collected = self.transactions.aggregate(Sum("amount"))["amount__sum"] or 0
		return self.amount_due - total_collected

	def __str__(self):
		return f"#Task {self.id}: customer ({self.customer.name}) - {self.amount_due}"


class Transaction(models.Model):
	collector = models.ForeignKey(User, related_name="transactions_collected", on_delete=models.CASCADE)

	task = models.ForeignKey(Task, related_name="transactions", on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.validate_transaction()

		is_collect_transaction = self.amount > 0
		if is_collect_transaction:
			self.validate_collect_transaction()
		else:
			self.validate_pay_transaction()

		super().save(*args, **kwargs)

		# mark task as collected
		self.task.is_collected = True
		self.task.save()

		# Add a signal to check if the threshold is exceeded
		if Transaction.is_threshold_exceeded(self.collector):
			self.collector.is_frozen = True
			self.collector.save()
		else:
			self.collector.is_frozen = False
			self.collector.save()

	def validate_transaction(self):
		if self.task is None:
			raise ValueError("Cannot create a transaction without a task.")
		if self.collector.is_manager:
			raise ValueError("A manager cannot collect/pay money.")
		if self.collector != self.task.collector:
			raise ValueError("The collector is not the collector of the task.")

	def validate_collect_transaction(self):
		if self.amount <= 0:
			raise ValueError("The amount should be greater than zero.")
		if self.task.remaining_amount() == 0:
			raise ValueError("The task is already collected.")
		if self.collector.is_frozen:
			raise ValueError("The user is frozen.")
		if self.amount < self.task.remaining_amount():
			raise ValueError("The amount is less than the remaining amount of the task.")
		if self.amount > self.task.remaining_amount():
			raise ValueError("The amount is more than the remaining amount of the task.")
		if self.task.is_collected:
			raise ValueError("The task is already collected.")

		return True

	def validate_pay_transaction(self):
		if self.amount >= 0:
			raise ValueError("The amount should be less than zero.")

		return True

	@classmethod
	def is_threshold_exceeded(cls, collector):
		"""
		Checks if the threshold is exceeded for the collector.
		"""
		x_days_ago = timezone.now() - timezone.timedelta(days=settings.DAYS_THRESHOLD)
		total_amount = (
			cls.objects.filter(collector=collector, timestamp__gte=x_days_ago).aggregate(Sum("amount"))[
				"amount__sum"
			]
			or 0
		)
		return total_amount > settings.USD_THRESHOLD

	@classmethod
	def get_total_amount(cls, user):
		return cls.objects.filter(collector=user).aggregate(Sum("amount"))["amount__sum"] or 0

	def __str__(self):
		return f"Transaction {self.id} - {self.amount}"
