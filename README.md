# EVE Healthcare - Diagnostic Booking API

A backend service for diagnostic test bookings and simulated payments, developed as part of the EVE Healthcare SDE Intern Backend Engineering Assignment.

The application provides REST APIs for user authentication, diagnostic centres, diagnostic tests, bookings, simulated payments, and payment webhooks.

---

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT Authentication
- SimpleJWT
- drf-spectacular / Swagger OpenAPI
- Pytest
- pytest-django

---

## Features

### Authentication
- User signup
- User login
- JWT-based authentication
- JWT access and refresh tokens
- Protected API endpoints
- Request validation

### Diagnostic Centres
- Create diagnostic centres
- List diagnostic centres
- Retrieve a diagnostic centre
- Update diagnostic centres
- Delete diagnostic centres
- Active/inactive centre support
- Staff-only modification access

### Diagnostic Tests
- Create diagnostic tests
- List diagnostic tests
- Retrieve a diagnostic test
- Update diagnostic tests
- Delete diagnostic tests
- Test pricing
- Active/inactive test support
- Prevention of duplicate tests within the same centre

### Booking System
- Authenticated users can create bookings
- Users can view their own bookings
- Appointment date/time validation
- Booking amount is calculated server-side
- Booking status management
- Booking cancellation
- Users cannot access other users' bookings

### Simulated Payment
- Mock payment processing
- SUCCESS and FAILED payment outcomes
- Payment amount linked to booking amount
- Booking status automatically updated after payment
- Payment cannot be processed for non-pending bookings

### Payment Webhook
- Payment status webhook
- Event-based processing
- Idempotent webhook handling
- Duplicate webhook events are safely ignored
- Database transaction handling
- Concurrent payment updates are protected using database row locking

### API Documentation
- Swagger UI
- OpenAPI schema

### Testing
- Unit/API tests using pytest
- Authentication tests
- Diagnostic API tests
- Booking tests
- Payment tests
- Webhook idempotency tests
- Authorization and edge-case tests

---

# Project Structure

```text
eve-healthcare-backend/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── diagnostics/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── bookings/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── payments/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Database Design

The application uses PostgreSQL as the primary database.

## Main Entities

```text
User
 │
 ├───────────────┐
 │               │
 ▼               ▼
Booking       Payment
 │               │
 │               │
 ├───────┐       │
 ▼       ▼       │
Centre  Test ◄───┘
              │
              ▼
       PaymentWebhookEvent
```

---

## User

The application uses Django's built-in user authentication model.

Users are authenticated using JWT tokens.

---

## DiagnosticCentre

Represents a diagnostic centre.

Main fields:

```text
id
name
location
is_active
created_at
updated_at
```

A diagnostic centre can offer multiple diagnostic tests.

---

## DiagnosticTest

Represents a diagnostic test offered by a diagnostic centre.

Main fields:

```text
id
centre
name
description
price
is_active
created_at
updated_at
```

A unique constraint prevents the same test from being created multiple times within the same diagnostic centre.

---

## Booking

Represents a user's diagnostic test appointment.

Main fields:

```text
id
user
centre
test
appointment_datetime
amount
status
created_at
updated_at
```

Supported booking statuses:

```text
PENDING
CONFIRMED
FAILED
CANCELLED
```

The booking amount is calculated from the test price on the server rather than being accepted from the client.

This prevents the client from manipulating the booking amount.

---

## Payment

Represents a simulated payment associated with a booking.

Main fields:

```text
id
booking
provider_payment_id
amount
status
created_at
updated_at
```

Supported payment statuses:

```text
PENDING
SUCCESS
FAILED
```

Each booking can have only one payment.

The payment amount is derived from the booking amount.

---

## PaymentWebhookEvent

Stores webhook events received from the simulated payment provider.

Main fields:

```text
id
event_id
payment
event_type
status
payload
created_at
```

`event_id` is unique.

This database-level uniqueness constraint provides protection against processing the same webhook event multiple times.

---

# Booking Flow

A new booking starts in the `PENDING` state.

```text
                    ┌───────────────┐
                    │    PENDING    │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
           Successful                Failed
             Payment                Payment
                │                       │
                ▼                       ▼
          CONFIRMED                  FAILED
```

A pending booking can also be cancelled:

```text
PENDING
   │
   ▼
CANCELLED
```

Booking status is not directly editable by the client.

---

# Authentication

The API uses JWT authentication.

A user first creates an account and then logs in to receive an access token.

The access token must be included in protected API requests:

```text
Authorization: Bearer <access_token>
```

---

# API Documentation

Swagger UI is available at:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

---

# API Endpoints

## Authentication

```text
POST /api/auth/signup/
POST /api/auth/login/
POST /api/auth/token/refresh/
GET  /api/auth/me/
```

---

## Diagnostic Centres

```text
GET    /api/diagnostics/centres/
POST   /api/diagnostics/centres/
GET    /api/diagnostics/centres/{id}/
PUT    /api/diagnostics/centres/{id}/
PATCH  /api/diagnostics/centres/{id}/
DELETE /api/diagnostics/centres/{id}/
```

Authenticated users can retrieve centres.

Only staff users can create, update, or delete centres.

---

## Diagnostic Tests

```text
GET    /api/diagnostics/tests/
POST   /api/diagnostics/tests/
GET    /api/diagnostics/tests/{id}/
PUT    /api/diagnostics/tests/{id}/
PATCH  /api/diagnostics/tests/{id}/
DELETE /api/diagnostics/tests/{id}/
```

Authenticated users can retrieve tests.

Only staff users can create, update, or delete tests.

---

## Bookings

```text
POST /api/bookings/
GET  /api/bookings/
GET  /api/bookings/{id}/
POST /api/bookings/{id}/cancel/
```

Users can only access their own bookings.

---

## Payments

```text
POST /api/payments/
GET  /api/payments/{id}/
```

---

## Payment Webhook

```text
POST /api/payments/webhook/
```

The webhook accepts payment-status updates from the simulated payment provider.

Repeated webhook events with the same `event_id` are safely ignored.

---

# Example API Requests

## Signup

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "Password123"
}
```

---

## Login

```json
{
    "username": "john",
    "password": "Password123"
}
```

The login response provides JWT access and refresh tokens.

Use the access token for authenticated API requests.

---

## Create Diagnostic Centre

Staff users can create a diagnostic centre.

```json
{
    "name": "EVE Diagnostics Jaipur",
    "location": "Jaipur, Rajasthan",
    "is_active": true
}
```

---

## Create Diagnostic Test

```json
{
    "centre": 1,
    "name": "CBC",
    "description": "Complete Blood Count",
    "price": "500.00",
    "is_active": true
}
```

---

## Create Booking

```json
{
    "centre": 1,
    "test": 1,
    "appointment_datetime": "2026-10-10T10:00:00+05:30"
}
```

The server determines the booking amount from the selected diagnostic test.

The client cannot directly set:

```text
amount
status
user
```

---

## Simulated Successful Payment

```json
{
    "booking_id": 1,
    "simulated_status": "SUCCESS"
}
```

Result:

```text
Payment → SUCCESS
Booking → CONFIRMED
```

---

## Simulated Failed Payment

```json
{
    "booking_id": 2,
    "simulated_status": "FAILED"
}
```

Result:

```text
Payment → FAILED
Booking → FAILED
```

---

## Payment Webhook

Example webhook:

```json
{
    "event_id": "evt_001",
    "event_type": "payment.updated",
    "payment_id": "provider-payment-uuid",
    "status": "SUCCESS"
}
```

After successful processing:

```text
Payment → SUCCESS
Booking → CONFIRMED
```

If the exact same webhook is received again using the same `event_id`, it is treated as a duplicate and is not processed again.

---

# Webhook Idempotency

Webhook idempotency is implemented using a unique `event_id`.

Example:

```text
First request

event_id = evt_001
        │
        ▼
Create webhook event
        │
        ▼
Update payment
        │
        ▼
Update booking
```

If the same event is received again:

```text
Second request

event_id = evt_001
        │
        ▼
Event already exists
        │
        ▼
Ignore duplicate
```

This prevents duplicate processing and protects booking/payment state.

The payment row is also locked during processing using a database transaction and row-level locking.

---

# Authorization and Security

The API implements ownership checks for user-specific resources.

For example, a user cannot access another user's booking:

```text
User A
  │
  └── Booking #1

User B
  │
  └── Booking #2
```

If User A requests:

```text
GET /api/bookings/2/
```

the API does not expose User B's booking.

Similarly, users cannot directly modify booking status.

Booking confirmation and failure are controlled by the payment flow.

Diagnostic centre and test modifications are restricted to staff users.

---

# Validation and Edge Cases

The API handles several invalid scenarios, including:

- Invalid booking IDs
- Past appointment dates
- Inactive diagnostic centres
- Inactive diagnostic tests
- Test/centre mismatch
- Unauthorized resource access
- Unauthorized diagnostic centre/test modification
- Payment for non-existent bookings
- Payment for non-pending bookings
- Repeated payment attempts
- Repeated webhook events
- Invalid webhook payment IDs

---

# Local Development Setup

## Prerequisites

Make sure the following are installed:

- Python
- PostgreSQL
- Git

Docker is not required to run the project locally.

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd eve-healthcare-backend
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 4. Configure PostgreSQL

Create a PostgreSQL database for the project.

Example:

```text
Database: eve_healthcare
User: eve_admin
Host: localhost
Port: 5432
```

---

## 5. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=eve_healthcare
DB_USER=eve_admin
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

Do not commit the `.env` file to Git.

---

## 6. Run migrations

```powershell
python manage.py migrate
```

---

## 7. Create an admin user

```powershell
python manage.py createsuperuser
```

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

---

## 8. Start the development server

```powershell
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# Running Tests

Run the complete test suite:

```powershell
pytest -v
```

Run Django system checks:

```powershell
python manage.py check
```

Check for model changes that require migrations:

```powershell
python manage.py makemigrations --check
```

---

# Testing Coverage

The automated tests cover:

### Authentication

- User registration
- Authentication
- Protected endpoints

### Diagnostics

- Centre listing
- Staff-only modification
- Test creation

### Bookings

- Booking creation
- Price calculation
- Invalid appointment time
- User ownership
- Booking cancellation
- Invalid booking IDs
- Unauthorized status modification

### Payments

- Successful payment
- Failed payment
- Invalid booking
- Repeated payment attempts
- Booking status updates

### Webhooks

- Successful webhook processing
- Payment status update
- Booking status update
- Duplicate webhook handling
- Idempotency

---

# Important Design Decisions

## Server-side payment amount

The client does not provide the payment amount.

Instead:

```text
DiagnosticTest.price
        │
        ▼
Booking.amount
        │
        ▼
Payment.amount
```

This prevents clients from manipulating the price.

---

## Booking ownership

Bookings are filtered by the authenticated user.

This prevents users from accessing other users' bookings.

---

## Database transactions

Payment and webhook operations use database transactions.

This helps maintain consistency when updating:

```text
Payment
+
Booking
+
PaymentWebhookEvent
```

---

## Row-level locking

Payment processing uses database row locking for the relevant payment/booking records.

This reduces the risk of concurrent requests changing the same payment or booking incorrectly.

---

## Webhook idempotency

Webhook events have a unique `event_id`.

This means the same provider event cannot be inserted and processed repeatedly.

---

# Assumptions

- PostgreSQL is used as the primary database.
- Django's built-in User model is sufficient for this assignment.
- Payment processing is simulated and does not connect to a real payment gateway.
- Only staff users can modify diagnostic centres and tests.
- Users can access only their own bookings and payments.
- Booking amount is captured from the test price when the booking is created.
- Payment amount is based on the booking amount.
- Payment webhook requests are assumed to originate from the simulated payment provider.
- Webhook signature verification is not implemented because the assignment uses a simulated payment provider.
- Appointment availability/slot capacity is outside the scope of this assignment.

---

# Future Improvements

If more development time were available, the following improvements could be added:

- Payment provider signature verification
- Redis-based rate limiting
- Redis caching
- Celery/background jobs
- Structured JSON logging
- Webhook retry and backoff handling
- Appointment slot availability management
- Real payment provider integration
- Improved refresh-token management
- Docker and docker-compose configuration
- Production deployment configuration
- Monitoring and application metrics
- More extensive integration and concurrency tests

---

# Bonus Engineering

The project includes several optional engineering improvements:

- Swagger/OpenAPI documentation
- Automated tests
- Pagination
- Database transactions
- Row-level locking
- Idempotent webhook processing
- Ownership-based authorization
- Separation of serializers, views, and service-layer business logic

---

# Submission

The repository contains:

```text
README.md
requirements.txt
.gitignore
.env.example
Source code
Tests
```

The project is designed to run locally using Django and PostgreSQL without requiring Docker.

---

## Author

Developed as part of the EVE Healthcare SDE Intern Backend Engineering Assignment.
