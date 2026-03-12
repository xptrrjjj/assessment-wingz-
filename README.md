# Wingz Ride Management API

RESTful API built with Django REST Framework for managing ride information. Provides a paginated, filterable, and sortable ride list with optimized query performance.

## Architecture

```
src/
├── core/                  # Project configuration
│   ├── settings/          # Split settings (base, development, staging, production)
│   ├── api/               # DRF config: router, pagination, permissions, error handling
│   └── urls.py            # Root URL configuration
├── modules/               # Feature modules (bounded contexts)
│   ├── accounts/          # User model, JWT authentication
│   └── rides/             # Ride, RideEvent models, selectors, API views
├── shared/                # Cross-cutting: base model, error system
└── tests/                 # Test suite with factories
```

**Key patterns:**
- **Selectors** for read queries — encapsulate queryset logic with `select_related`/`prefetch_related`
- **Plain serializers** (not ModelSerializer) to decouple API shape from DB schema
- **Split settings** with environment-based overlay loading
- **Standard error format** — all errors return `{"error": {"type", "detail", "extra"}}`

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone and enter project
git clone https://github.com/xptrrjjj/assessment-wingz-.git
cd assessment-wingz

# Create virtual environment
python -m venv .venv

# Activate (choose your OS)
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows CMD
.venv\Scripts\Activate.ps1       # Windows PowerShell

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env as needed (defaults work for local development)

# Run migrations
python src/manage.py migrate

# Seed sample data (7 users, 50 rides with events)
python src/manage.py seed_data

# Create a superuser for admin access
python src/manage.py createsuperuser

# Start the server
python src/manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Settings overlay (`development`, `staging`, `production`) |
| `DJANGO_SECRET_KEY` | `change-me` | Secret key (must change in production) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DB_ENGINE` | `django.db.backends.sqlite3` | Database engine |
| `DB_NAME` | `db.sqlite3` | Database name/path |
| `DB_USER` | | Database user |
| `DB_PASSWORD` | | Database password |
| `DB_HOST` | | Database host |
| `DB_PORT` | | Database port |
| `LOG_LEVEL` | `INFO` | Logging level |

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/accounts/token/` | Obtain JWT access + refresh tokens |
| POST | `/api/v1/accounts/token/refresh/` | Refresh an access token |

**Obtain tokens:**

```bash
curl -X POST http://localhost:8000/api/v1/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Ride List API

All ride endpoints require authentication (JWT Bearer token) and `admin` role.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rides/` | List rides (paginated) |
| GET | `/api/v1/rides/{id_ride}/` | Retrieve a single ride |

**List rides with all features:**

```bash
curl http://localhost:8000/api/v1/rides/?status=en-route&ordering=-pickup_time&page_size=10 \
  -H "Authorization: Bearer <access_token>"
```

**Response:**

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/rides/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id_ride": 42,
      "status": "en-route",
      "id_rider": {
        "id_user": 5,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com"
      },
      "id_driver": {
        "id_user": 2,
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com"
      },
      "pickup_latitude": 40.7128,
      "pickup_longitude": -74.006,
      "dropoff_latitude": 40.758,
      "dropoff_longitude": -73.9855,
      "pickup_time": "2024-01-15T14:30:00Z",
      "todays_ride_events": [
        {
          "id_ride_event": 101,
          "description": "Status changed to pickup",
          "created_at": "2024-01-15T14:35:00Z"
        }
      ],
      "distance": null
    }
  ]
}
```

### Filtering

| Parameter | Example | Description |
|-----------|---------|-------------|
| `status` | `?status=en-route` | Filter by ride status (`en-route`, `pickup`, `dropoff`) |
| `id_rider__email` | `?id_rider__email=jane@example.com` | Filter by exact rider email |
| `id_rider__email__icontains` | `?id_rider__email__icontains=jane` | Filter by partial rider email |

### Sorting

| Parameter | Example | Description |
|-----------|---------|-------------|
| `ordering` | `?ordering=pickup_time` | Sort by pickup time ascending |
| `ordering` | `?ordering=-pickup_time` | Sort by pickup time descending (default) |
| `ordering` + `lat`/`lng` | `?lat=40.7128&lng=-74.006&ordering=distance` | Sort by distance to pickup |

**Sort by distance to a GPS position:**

```bash
curl "http://localhost:8000/api/v1/rides/?lat=40.7128&lng=-74.0060&ordering=distance" \
  -H "Authorization: Bearer <access_token>"
```

When `lat` and `lng` are provided, each ride includes a `distance` field (in km) computed via the Haversine formula.

### Pagination

| Parameter | Default | Max | Description |
|-----------|---------|-----|-------------|
| `page` | 1 | - | Page number |
| `page_size` | 20 | 100 | Results per page |

### API Documentation

| Endpoint | Description |
|----------|-------------|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | Raw OpenAPI schema |

### Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "type": "ValidationError",
    "detail": "lat must be between -90 and 90.",
    "extra": {
      "fields": {
        "lat": ["95.0"]
      }
    }
  }
}
```

| Status Code | Type | When |
|-------------|------|------|
| 400 | `ValidationError` | Invalid query parameters (bad lat/lng, etc.) |
| 401 | `AuthenticationFailed` | Missing or invalid JWT token |
| 403 | `PermissionDenied` | Authenticated but not an admin |
| 404 | `NotFound` | Ride ID does not exist |

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=modules --cov-report=term-missing

# Run specific test file
pytest src/tests/modules/rides/test_views.py

# Run specific test class
pytest src/tests/modules/rides/test_views.py::TestRideListViewFiltering
```

**Test suite:** 53 tests covering models, selectors, views (auth, filtering, sorting, pagination, error handling, query count).

## Design Decisions and Trade-offs

### Query Optimization (2-3 queries for the ride list)

The ride list API achieves a fixed query budget regardless of result count:

1. **Query 1** — `SELECT rides JOIN users (rider) JOIN users (driver)` via `select_related("id_rider", "id_driver")`. This fetches rides with both related users in a single SQL JOIN.

2. **Query 2** — `SELECT ride_events WHERE id_ride IN (...) AND created_at >= now-24h` via `Prefetch` with a filtered queryset and `to_attr="todays_ride_events"`. This fetches only the last 24 hours of events in one batched query, regardless of how many total events exist.

3. **Query 3** — `SELECT COUNT(*) FROM rides` (pagination count, automatic from DRF).

This avoids the N+1 problem entirely. Without `select_related`, each ride would trigger 2 additional queries for rider and driver. Without `Prefetch`, each ride would trigger a query for its events.

### Haversine Distance Sorting

Distance sorting is implemented as a SQL annotation using Django ORM math functions (`ACos`, `Cos`, `Sin`, `Radians`, `F`, `Value`). The Haversine formula computes great-circle distance between two GPS coordinates.

**Why annotation instead of in-memory sorting:**
- SQL-level `ORDER BY distance LIMIT/OFFSET` means pagination works correctly
- No need to load all rides into memory for sorting
- The database handles the math, keeping Python memory usage constant

### Prefetch with Filtered Queryset for 24-hour Events

The `todays_ride_events` field uses `Prefetch` with a filtered queryset rather than filtering in the serializer:

```python
Prefetch(
    "ride_events",
    queryset=RideEvent.objects.filter(created_at__gte=twenty_four_hours_ago),
    to_attr="todays_ride_events",
)
```

**Why this approach:**
- The filter happens in SQL, so Django never loads old events into memory
- With a large `ride_events` table, this is critical — it fetches only relevant rows
- `to_attr` stores the result as a plain list, avoiding further queryset evaluation

### Plain Serializers over ModelSerializer

Serializers use `serializers.Serializer` instead of `ModelSerializer`:

- Decouples API response shape from database schema
- Explicit field declarations make the API contract visible in code
- Prevents accidental exposure of model fields when the model changes

## Bonus SQL

Raw SQL query that returns trips longer than 1 hour from pickup to dropoff, grouped by month and driver:

```sql
SELECT
    strftime('%Y-%m', pickup_event.created_at) AS month,
    u.first_name || ' ' || u.last_name         AS driver,
    COUNT(*)                                    AS trip_count
FROM ride_events AS pickup_event
JOIN ride_events AS dropoff_event
    ON pickup_event.id_ride = dropoff_event.id_ride
JOIN rides AS r
    ON r.id_ride = pickup_event.id_ride
JOIN users AS u
    ON u.id_user = r.id_driver
WHERE pickup_event.description  = 'Status changed to pickup'
  AND dropoff_event.description = 'Status changed to dropoff'
  AND (
      julianday(dropoff_event.created_at) - julianday(pickup_event.created_at)
  ) * 24 > 1
GROUP BY month, driver
ORDER BY month, driver;
```

**For PostgreSQL / MySQL, replace the date and time functions:**

```sql
-- PostgreSQL version
SELECT
    to_char(pickup_event.created_at, 'YYYY-MM') AS month,
    u.first_name || ' ' || u.last_name           AS driver,
    COUNT(*)                                      AS trip_count
FROM ride_events AS pickup_event
JOIN ride_events AS dropoff_event
    ON pickup_event.id_ride = dropoff_event.id_ride
JOIN rides AS r
    ON r.id_ride = pickup_event.id_ride
JOIN users AS u
    ON u.id_user = r.id_driver
WHERE pickup_event.description  = 'Status changed to pickup'
  AND dropoff_event.description = 'Status changed to dropoff'
  AND EXTRACT(EPOCH FROM (dropoff_event.created_at - pickup_event.created_at)) / 3600 > 1
GROUP BY month, driver
ORDER BY month, driver;
```

**How it works:**

1. **Self-join `ride_events`** — joins the table to itself to pair pickup and dropoff events for the same ride (`pickup_event.id_ride = dropoff_event.id_ride`)
2. **Filter by description** — pickup event has `"Status changed to pickup"`, dropoff event has `"Status changed to dropoff"`
3. **Calculate duration** — computes the time difference between dropoff and pickup timestamps, filters for trips exceeding 1 hour
4. **Group** — groups by calendar month (YYYY-MM format) and driver full name
5. **Result** — count of trips per month per driver where the trip duration exceeded 1 hour

**Sample output:**

| month | driver | trip_count |
|-------|--------|------------|
| 2024-01 | Chris H | 4 |
| 2024-01 | Howard Y | 5 |
| 2024-01 | Randy W | 2 |
| 2024-02 | Chris H | 7 |
| 2024-02 | Howard Y | 5 |
| 2024-03 | Chris H | 2 |
| 2024-03 | Howard Y | 2 |
| 2024-03 | Randy W | 11 |
| 2024-04 | Howard Y | 7 |
| 2024-04 | Randy W | 3 |
