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


class CollectSchema(Schema):
	task_id: int
	amount: float
	timestamp: datetime


class PaySchema(Schema):
	amount: float


api = NinjaAPI()


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
		}
		for task in tasks
	]


@api.get("/next_task", response={200: Optional[TaskSchema]}, auth=BearerAuth())
def get_next_task(request):
	task = Task.objects.filter(collector=request.auth, is_collected=False).order_by("amount_due_at").first()
	if task:
		return {
			"id": task.id,
			"collector": task.collector.id,
			"customer": task.customer.id,
			"amount_due": task.remaining_amount(),
			"amount_due_at": task.amount_due_at,
			"is_collected": task.is_collected,
		}

	return None


@api.get("/status", auth=BearerAuth())
def status(request):
	return {"is_frozen": request.auth.is_frozen}


@api.post("/collect", auth=BearerAuth())
def collect(request, payload: CollectSchema):
	"""Cash collector collects the amount of money from the customer."""
	task = get_object_or_404(Task, id=payload.task_id, collector=request.auth)
	task_manager = task.manager
	# create a transaction
	transaction = Transaction.objects.create(
		collector=request.auth,
		manager=task_manager,
		task=task,
		amount=Decimal(payload.amount),
		timestamp=payload.timestamp,
	)
	return {
		"message": f"Transaction created with id {transaction.id} \nAmount: {payload.amount} \nTask: {task.id}"
	}


@api.post("/pay", auth=BearerAuth())
def pay(request, payload: PaySchema):
	"""Cash collector pays the amount of money to the manager."""
	amount = Decimal(payload.amount)
	request.auth.pay_to_manager(amount)
	return {"message": f"Paid {amount} to the manager {request.auth.manager.first_name}"}
