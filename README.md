# Restful Booker API Test Automation Framework

API test automation framework for the Restful Booker service, built with Python, `pytest`, and `requests`.

The framework focuses on transactional API workflows, authentication management, concurrency behavior, idempotency, schema validation, and resilience when testing against a shared public environment.

## Project Structure

```text
restful-booker-tests/
├── framework/
│   ├── auth.py
│   ├── client.py
│   ├── data.py
│   └── schemas.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_booking_lifecycle.py
│   ├── test_client_auth.py
│   ├── test_concurrency.py
│   ├── test_idempotency.py
│   └── test_schemas.py
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- pip

## Setup

Clone the repository and move into the project directory.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a local `.env` file based on `.env.example`.

```bash
cp .env.example .env
```

Populate the required Restful Booker credentials in `.env`.

The `.env` file is excluded from version control so credentials are not committed to the repository.

## Running the Tests

From the project root, run:

```bash
python3 -m pytest -v
```

Using `python3 -m pytest` ensures the project root is available to Python when importing the local `framework` package.

## Test Coverage

The suite contains 18 automated tests covering the following areas.

### Booking Lifecycle

Tests exercise the main booking workflow:

- Create a booking
- Retrieve the created booking
- Update an existing booking
- Delete a booking

### Authentication and Token Management

Authentication is centralized rather than duplicated throughout individual tests.

The suite verifies concurrent token requests and ensures multiple callers can share a single token refresh operation.

### Authentication Recovery

The API client handles an authentication failure by refreshing its token and retrying the request.

Retry behavior is deliberately bounded so a persistent authentication failure does not result in an infinite retry loop.

### Concurrency

Concurrent update behavior is exercised using simultaneous PUT operations.

The test focuses on safely executing competing transactional operations against the shared API environment.

### Idempotency

PUT behavior is tested by repeating the same update and validating that the resulting booking state remains consistent.

PATCH behavior is also tested to ensure fields omitted from a partial update remain unchanged.

### Schema Validation

Booking responses are validated using JSON Schema.

Validation includes:

- Required top-level fields
- Required nested booking-date fields
- String and boolean types
- Integer validation for `totalprice`
- Non-negative pricing
- ISO date formats
- Rejection of unexpected properties
- Checkout occurring after check-in

In addition to structural JSON Schema validation, the framework performs the cross-field business-rule check that checkout must be later than check-in.

## Shared Environment Considerations

Restful Booker is a public shared sandbox, so tests should not depend on global environment state remaining unchanged.

Tests create and operate on their own booking data where possible and validate the state associated with those transactions rather than assuming exclusive access to the environment.

This reduces coupling between tests and makes failures easier to distinguish from interference caused by other users of the public service.

## Test Data

Test data creation is centralized in the framework to reduce duplication and keep test cases focused on behavior rather than payload construction.

## Latest Test Result

Full suite verification:

```text
18 collected
18 passed
```

The final verification run completed successfully with all tests passing.

## Technologies

- Python
- pytest
- requests
- jsonschema
- python-dotenv