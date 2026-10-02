# EVE Healthcare — Diagnostic Booking Backend

A Django REST Framework backend for diagnostic centres, diagnostic tests, bookings, simulated payments, payment webhooks, JWT authentication, validation, tests, Swagger/OpenAPI documentation, pagination, and Docker support.

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- SimpleJWT
- drf-spectacular / Swagger UI
- pytest
- Docker / Docker Compose

## Features

- JWT signup, login, refresh, and protected `/me/` endpoint
- Diagnostic centres and tests with pricing
- Staff-only diagnostic modifications
- Pagination
- Booking creation, ownership isolation, validation, and cancellation
- Server-side booking price snapshot
- Simulated SUCCESS / FAILED payments
- Transactional payment processing
- Idempotent payment webhooks with unique event IDs
- Swagger/OpenAPI documentation
- Automated tests
- Dockerized Django + PostgreSQL environment

## Project Structure

```text
eve-healthcare-backend/
├── accounts/
├── bookings/
├── config/
├── diagnostics/
├── payments/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

# Running Locally

## Prerequisites

- Python 3.12+
- PostgreSQL
- Git

## Setup

```powershell
git clone <your-github-repository-url>
cd eve-healthcare-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=eve_healthcare
DB_USER=eve_admin
DB_PASSWORD=your-postgresql-password
DB_HOST=localhost
DB_PORT=5432
```

Apply migrations and start Django:

```powershell
python manage.py migrate
python manage.py runserver
```

API: `http://localhost:8000/`

Swagger: `http://localhost:8000/api/docs/`

Never commit the real `.env`.

# Running with Docker

Docker Compose runs two services:

```text
web → Django + Django REST Framework
db  → PostgreSQL
```

Inside Docker, Django connects to PostgreSQL through the Compose service name:

```text
DB_HOST=db
DB_PORT=5432
```

## Prerequisites

- Docker Desktop

## Start

Create `.env` from `.env.example`, then run:

```powershell
docker compose up --build
```

API: `http://localhost:8000/`

Swagger: `http://localhost:8000/api/docs/`

## Migrations

```powershell
docker compose exec web python manage.py migrate
```

## Tests

```powershell
docker compose exec web pytest -v
```

## Django checks

```powershell
docker compose exec web python manage.py check
```

## Container status

```powershell
docker compose ps
```

## Stop

```powershell
docker compose down
```

To also delete the PostgreSQL Docker volume/data:

```powershell
docker compose down -v
```

> `docker compose down -v` removes the PostgreSQL data stored in the Docker volume.

# API Endpoints

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/signup/` | Register user |
| POST | `/api/auth/login/` | Obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh JWT |
| GET | `/api/auth/me/` | Current authenticated user |

## Diagnostics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/diagnostics/centres/` | List centres |
| POST | `/api/diagnostics/centres/` | Create centre — staff |
| GET | `/api/diagnostics/centres/{id}/` | Retrieve centre |
| PUT/PATCH | `/api/diagnostics/centres/{id}/` | Update centre — staff |
| DELETE | `/api/diagnostics/centres/{id}/` | Delete centre — staff |
| GET | `/api/diagnostics/tests/` | List tests |
| POST | `/api/diagnostics/tests/` | Create test — staff |
| GET | `/api/diagnostics/tests/{id}/` | Retrieve test |
| PUT/PATCH | `/api/diagnostics/tests/{id}/` | Update test — staff |
| DELETE | `/api/diagnostics/tests/{id}/` | Delete test — staff |

## Bookings

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/bookings/` | List current user's bookings |
| POST | `/api/bookings/` | Create booking |
| GET | `/api/bookings/{id}/` | Retrieve own booking |
| POST | `/api/bookings/{id}/cancel/` | Cancel pending booking |

PUT/PATCH is intentionally not exposed for bookings.

## Payments

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/payments/` | Create/process simulated payment |
| GET | `/api/payments/{id}/` | Retrieve payment |
| POST | `/api/payments/webhook/` | Process payment webhook |

# Authentication

JWT authentication is provided through SimpleJWT.

Use the returned access token on protected endpoints:

```http
Authorization: Bearer <access-token>
```

# Database Design

```text
User
 │
 └──< Booking >── DiagnosticTest >── DiagnosticCentre
          │
          └── Payment
                 │
                 └──< PaymentWebhookEvent
```

- **User:** authentication and booking ownership.
- **DiagnosticCentre:** diagnostic centre information and active status.
- **DiagnosticTest:** test information, price, and associated centre.
- **Booking:** user, test, centre, appointment date/time, amount, and status.
- **Payment:** simulated payment associated one-to-one with a booking.
- **PaymentWebhookEvent:** processed webhook event IDs for idempotency.

The booking amount is calculated server-side from the selected test price.

# Booking Flow

```text
Authenticated User
       ↓
Select Centre + Test
       ↓
Validate Centre/Test
       ↓
Validate Appointment Time
       ↓
Create Pending Booking
       ↓
Process Payment
       ├── SUCCESS → Booking confirmed
       └── FAILED  → Payment failed
```

# Payment Webhook Idempotency

Each webhook contains a unique event ID. Processed event IDs are stored so duplicate deliveries do not apply the same state transition again.

```text
Webhook Event
      ↓
Already processed?
   ├── Yes → Ignore
   └── No
        ↓
   Update Payment
        ↓
   Update Booking
        ↓
   Store Event ID
```

Payment and booking state changes are handled transactionally.

# Authorization & Security

- JWT authentication
- Protected booking/payment endpoints
- User ownership checks
- Staff-only diagnostic modifications
- Server-side price calculation
- Booking status validation
- Future appointment validation
- Transactional critical operations
- Database row locking where required
- Idempotent webhook processing
- Unique webhook event IDs
- `.env` excluded from Git
- `.env` excluded from Docker build context

# Edge Cases

The implementation handles:

- Duplicate signup email
- Invalid credentials
- Unauthorized protected access
- Unauthorized diagnostic modifications
- Invalid centre/test relationships
- Inactive centre/test
- Past appointments
- Invalid booking IDs
- Access to another user's booking
- Repeated cancellation
- Payment for another user's booking
- Payment for non-pending booking
- Invalid payment status
- Repeated payment processing
- Failed simulated payments
- Duplicate webhook events
- Unknown provider payment IDs
- Transaction conflicts/concurrent payment updates

# Testing

Local:

```powershell
pytest -v
python manage.py check
python manage.py makemigrations --check
```

Docker:

```powershell
docker compose exec web pytest -v
docker compose exec web python manage.py check
```

# Design Decisions

### Server-side booking amount
The booking amount comes from the selected test price rather than a client-supplied amount.

### Transactional operations
Critical booking/payment operations use database transactions.

### User-level booking isolation
Booking querysets and ownership checks prevent users from accessing other users' bookings.

### Controlled booking modification
Bookings do not expose arbitrary PUT/PATCH updates; controlled operations are used instead.

### Webhook idempotency
Unique event IDs prevent duplicate webhook delivery from re-applying the same state transition.

### Database locking
Payment operations use row-level locking where required to reduce race conditions.

### Dockerized environment
Docker Compose provides a consistent Django + PostgreSQL development environment.

# Environment Variables

`.env.example`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=eve_healthcare
DB_USER=eve_admin
DB_PASSWORD=your-postgresql-password
DB_HOST=localhost
DB_PORT=5432
```

For Docker, Compose overrides the Django container's database host to:

```text
DB_HOST=db
DB_PORT=5432
```

Never commit real credentials or secret keys.

# Future Improvements

- Real payment gateway integration
- Background jobs for payment processing
- Email/SMS booking notifications
- Appointment slot availability management
- Rate limiting
- Structured logging
- Production WSGI/ASGI server configuration
- Redis caching
- More granular permissions
- CI/CD pipeline
- Deployment configuration
- Monitoring and health-check endpoints

# API Documentation

Swagger/OpenAPI:

`http://localhost:8000/api/docs/`

# Quick Commands

## Local

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker

```powershell
docker compose up --build
```

## Docker tests

```powershell
docker compose exec web pytest -v
```

## Stop Docker

```powershell
docker compose down
```

# Assignment Focus

This implementation focuses on clean REST API design, authentication and authorization, relational database modeling, validation, transaction safety, payment state management, webhook idempotency, automated testing, API documentation, Dockerized development, and clear documentation.
