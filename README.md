# InstaCash

InstaCash is a simple cash collection system that allows users to collect cash from their customers and keep track of the cash collected. 
The system allows users to create customer accounts, record cash collections, and pay out cash to their managers.

## Deliverables

- [x] Implemented these basic api endpoints:
    - [x] `/collect` - POST - Collect cash from a customer
    - [x] `/pay` - POST - Pay out cash to a manager
    - [x] `/status` - GET - check if collector is frozen
    - [x] `/tasks` - GET - Get all tasks that's not collected yet
    - [x] `/next_task` - GET - Get the next task that's not collected yet
- [X] Basic authentication using **Bear Token**
- [x] Dockerized application for easy deployment
- [x] A RESTful API using DjangoNinja (DRF alternative) that leverages the Python type hints for request and response validation
- [x] API documentation using Swagger UI, find it at `api/docs`
- [x] Unit tests for the API endpoints, using `pytest` and DjangoNinja's `TestClient`
- [x] PostgreSQL database for data storage
- [x] **Code Quality:** Leverage `ruff` as a linter and formatter, `mypy` for static type checking
- [x] Use `pre-commit` to run the linter, formatter, and static type checker before committing the code, install it using `pre-commit install`

## Installation

### Docker

1. Clone the repository
2. Run `docker-compose up -d` to build and run the application
3. The application will be available at `http://localhost:8004`

#### Debugging

1. Find the container id using `docker ps`
2. Run `docker exec -it <container_id> bash` to enter the container
3. Or run `docker logs <container_id>` to view the logs

### Manual

1. Clone the repository
2. Create a virtual environment using `python -m venv venv`
3. Install the dependencies using `python -m pip install -r requirements.txt`
4. Run the application using `python manage.py runserver`
5. The application will be available at `http://localhost:8000`

**Note:** You need to have PostgreSQL installed and running on your machine. 
Update the database settings in `instacash/settings.py` to match your database configuration.

## Testing

Run the tests using `pytest`:

```bash
pytest -vvs
```

`cashcollector`, is a pytest marker that runs the tests for the `cashcollector` app only.

```bash
pytest -vvs -m cashcollector
```
