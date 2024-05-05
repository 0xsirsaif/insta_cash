import pytest
from django.utils import timezone
from ninja.testing import TestClient

from cash_collector.api import api as router
from cash_collector.models import Customer, Task, User


@pytest.fixture(scope="function")
def manager():
	manager = User.objects.create(username="testmanager", auth_token="testtoken1", is_manager=True)
	return manager


@pytest.fixture(scope="function")
def user(manager):
	user = User.objects.create(username="testuser", auth_token="testtoken2", manager=manager)
	return user


@pytest.fixture(scope="function")
def customer():
	customer = Customer.objects.create(name="testcustomer")
	return customer


@pytest.fixture(scope="module")
def client():
	return TestClient(router)


@pytest.fixture(scope="function")
def task(user, manager, customer):
	task = Task.objects.create(
		collector=user, manager=manager, customer=customer, amount_due=20_000.0, amount_due_at=timezone.now()
	)
	return task


@pytest.mark.django_db()
@pytest.mark.cashcollector()
def test_collect_task(client, manager, user, task):
	response = client.post(
		"collect",
		json={"task_id": task.id, "amount": 20_000.0, "timestamp": timezone.now().isoformat()},
		headers={"Authorization": f"Bearer {user.auth_token}"},
	)
	assert response.status_code == 200
	assert Task.objects.get(id=task.id).is_collected is True
	assert Task.objects.get(id=task.id).remaining_amount() == 0.0

	with pytest.raises(ValueError, match="The task is already collected."):
		client.post(
			"collect",
			json={"task_id": task.id, "amount": 10000.0, "timestamp": timezone.now().isoformat()},
			headers={"Authorization": f"Bearer {user.auth_token}"},
		)


@pytest.mark.django_db()
@pytest.mark.cashcollector()
def test_pay_task(client, manager, user, task):
	response = client.post(
		"pay",
		json={"task_id": task.id, "amount": 20_000.0, "timestamp": timezone.now().isoformat()},
		headers={"Authorization": f"Bearer {user.auth_token}"},
	)
	assert response.status_code == 200
	assert Task.objects.get(id=task.id).is_collected is True


@pytest.mark.django_db()
@pytest.mark.cashcollector()
def test_collect_threshold_exceeded(client, manager, user, task):
	two_days_ago = timezone.now() - timezone.timedelta(days=2)
	response = client.post(
		"collect",
		json={"task_id": task.id, "amount": 20_000.0, "timestamp": two_days_ago.isoformat()},
		headers={"Authorization": f"Bearer {user.auth_token}"},
	)
	assert response.status_code == 200
	assert Task.objects.get(id=task.id).is_collected is True
	assert User.objects.get(id=user.id).is_frozen is True

	# perform pay
	response = client.post(
		"pay",
		json={"task_id": task.id, "amount": 20_000.0, "timestamp": timezone.now().isoformat()},
		headers={"Authorization": f"Bearer {user.auth_token}"},
	)
	assert response.status_code == 200
	assert User.objects.get(id=user.id).is_frozen is False
