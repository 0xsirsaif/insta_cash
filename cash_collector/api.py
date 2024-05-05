from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import HttpBearer

from .models import Task, Transaction, User


class BearerAuth(HttpBearer):
	def authenticate(self, request, token):
		try:
			return User.objects.get(auth_token=token)
		except User.DoesNotExist:
			return None


class TaskSchema(Schema):
	id: int
	collector: int
	customer: int
	amount_due: float
	amount_due_at: datetime
	is_collected: bool
	related_transaction: int


class CollectSchema(Schema):
	task_id: int
	amount: float
	timestamp: datetime


class PaySchema(Schema):
	task_id: int
	amount: float
	timestamp: datetime


api = NinjaAPI(version="1.0.0", urls_namespace="cash_collector")


@api.get("/tasks", response={200: Optional[list[TaskSchema]]}, auth=BearerAuth())
def get_tasks(request):
	tasks = Task.objects.filter(collector=request.auth, is_collected=True)
	return [
		{
			"id": task.id,
			"collector": task.collector.id,
			"customer": task.customer.id,
			"amount_due": task.amount_due,
			"amount_due_at": task.amount_due_at,
			"is_collected": task.is_collected,
			"related_transaction": Transaction.objects.filter(task=task).id,
		}
		for task in tasks
	]


@api.get("/next_task", response={200: Optional[TaskSchema]}, auth=BearerAuth())
def get_next_task(request):
	task = Task.objects.filter(collector=request.auth, is_collected=False).order_by("amount_due_at").first()
	related_transaction = Transaction.objects.filter(task=task)
	if task:
		return {
			"id": task.id,
			"collector": task.collector.id,
			"customer": task.customer.id,
			"amount_due": task.remaining_amount(),
			"amount_due_at": task.amount_due_at,
			"is_collected": task.is_collected,
			"related_transaction": related_transaction,
		}

	return None


@api.get("/status", auth=BearerAuth())
def status(request):
	return {"is_frozen": request.auth.is_frozen}


@api.post("/collect", auth=BearerAuth())
def collect(request, payload: CollectSchema):
	"""Cash collector collects the amount of money from the customer."""
	task = get_object_or_404(Task, id=payload.task_id, collector=request.auth)
	# create a transaction
	transaction = Transaction.objects.create(
		collector=request.auth,
		task=task,
		amount=Decimal(payload.amount),
		timestamp=payload.timestamp,
	)
	return {"message": f"Transaction created with id {transaction.id}"}


@api.post("/pay", auth=BearerAuth())
def pay(request, payload: PaySchema):
	"""Cash collector pays the amount of money to the manager."""
	task = get_object_or_404(Task, id=payload.task_id, collector=request.auth)
	transaction = Transaction.objects.create(
		collector=request.auth,
		task=task,
		amount=-Decimal(payload.amount),
		timestamp=payload.timestamp,
	)
	return {"message": f"Transaction created with id {transaction.id}"}
