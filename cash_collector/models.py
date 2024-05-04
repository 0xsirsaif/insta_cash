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

	def clean(self):
		super().clean()

		# Add custom validation for manager field
		if self.is_manager and self.manager is not None:
			raise ValidationError({"manager": _("A manager cannot have a manager.")})

	def __str__(self):
		return self.username

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

	def pay_to_manager(self, amount):
		"""
		Pay the manager the amount of money.
		"""
		if self.is_manager:
			raise ValueError("The user is a manager.")

		transaction = Transaction.objects.create(
			collector=self,
			manager=self.manager,
			amount=-amount,
		)

		# check if the threshold is exceeded
		if Transaction.is_threshold_exceeded(self):
			self.is_frozen = True
			self.save()
		else:
			# unfreeze the user
			self.is_frozen = False

		return transaction


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
		total_collected = self.transactions.filter(deleted=False).aggregate(Sum("amount"))["amount__sum"] or 0
		return self.amount_due - total_collected

	def __str__(self):
		return f"#Task {self.id}: customer ({self.customer.name}) - {self.amount_due}"


class Transaction(models.Model):
	collector = models.ForeignKey(User, related_name="transactions_collected", on_delete=models.CASCADE)
	manager = models.ForeignKey(User, related_name="transactions_paid", on_delete=models.CASCADE)
	task = models.ForeignKey(Task, related_name="transactions", on_delete=models.CASCADE, null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	timestamp = models.DateTimeField(auto_now_add=True)
	deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		is_pay = self.amount < 0
		if not is_pay and self.collector.is_frozen:
			raise ValueError("Cannot add a new transaction. The user is frozen.")
		if not is_pay and self.amount > self.task.amount_due:
			raise ValueError(
				"Cannot add a new transaction. The transaction amount is more than the amount due in the task."
			)
		super().save(*args, **kwargs)

	@classmethod
	def is_threshold_exceeded(cls, collector):
		"""
		Checks if the threshold is exceeded for the collector.
		"""
		x_days_ago = timezone.now() - timezone.timedelta(days=settings.DAYS_THRESHOLD)
		total_amount = (
			cls.objects.filter(collector=collector, timestamp__gte=x_days_ago, deleted=False).aggregate(
				Sum("amount")
			)["amount__sum"]
			or 0
		)
		return total_amount > settings.USD_THRESHOLD

	@classmethod
	def get_total_amount(cls, user):
		return cls.objects.filter(collector=user).aggregate(Sum("amount"))["amount__sum"] or 0

	def __str__(self):
		return f"Transaction {self.id} - {self.amount}"
