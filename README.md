# 📚 Library Management System

A **production-grade** RESTful API built with Flask, containerized with Docker, orchestrated with Kubernetes, and delivered via a full CI/CD pipeline with observability.

---

## 🏗️ Architecture Overview

```
Internet → Nginx (reverse proxy + rate limiting)
             │
             ↓
        Flask App (gunicorn, 4 workers)
             │
      ┌──────┴──────┐
      ↓             ↓
 PostgreSQL    Prometheus
  (data)       (metrics)
                   │
               Grafana
              (dashboards)
```

### Stack
| Layer | Technology |
|-------|-----------|
| API | Flask 3.0 + SQLAlchemy |
| Database | PostgreSQL 15 |
| Server | Gunicorn (4 workers) |
| Reverse Proxy | Nginx 1.25 |
| Containerization | Docker (multi-stage) |
| Orchestration | Kubernetes + HPA |
| CI/CD | GitHub Actions |
| Metrics | Prometheus + Grafana |

---

## 🚀 Quick Start

### 1. Local Development (Python)
```bash
# Install deps
make install

# Run tests
make test

# Start dev server
python run.py
```

### 2. Docker Compose (Recommended)
```bash
# Start the full stack
make up

# Seed sample data
make seed

# View logs
make logs
```

**URLs:**
- API: http://localhost:5000
- Health: http://localhost:5000/health
- Metrics: http://localhost:5000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## 📖 API Reference

### Books `/api/books`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | List all books (supports `?q=` and `?genre=`) |
| POST | `/api/books` | Add a new book |
| GET | `/api/books/:id` | Get book by ID |
| PUT | `/api/books/:id` | Update book |
| DELETE | `/api/books/:id` | Remove book |

**Create book:**
```json
POST /api/books
{
  "isbn": "9780132350884",
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "genre": "Engineering",
  "year": 2008,
  "copies": 3
}
```

### Members `/api/members`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/members` | List active members |
| POST | `/api/members` | Register new member |
| GET | `/api/members/:id` | Get member |
| PUT | `/api/members/:id` | Update member |
| DELETE | `/api/members/:id` | Deactivate member |

### Loans `/api/loans`
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/loans` | List all loans (supports `?status=active/returned/overdue`) |
| POST | `/api/loans` | Issue a loan |
| POST | `/api/loans/:id/return` | Return a book |
| GET | `/api/loans/overdue` | Get all overdue loans |

**Issue a loan:**
```json
POST /api/loans
{
  "book_id": 1,
  "member_id": 2
}
```

### System
| Endpoint | Description |
|----------|-------------|
| GET `/health` | Liveness probe (DB check) |
| GET `/ready` | Readiness probe |
| GET `/metrics` | Prometheus metrics |

---

## 🔄 CI/CD Pipeline

```
Push to main
    │
    ▼
[Job 1] Test
  ├─ flake8 lint
  ├─ pytest + coverage
  └─ Coverage upload to Codecov
    │
    ▼
[Job 2] Security
  ├─ Bandit (Python SAST)
  ├─ Safety (dependency CVEs)
  └─ Hadolint (Dockerfile)
    │
    ▼
[Job 3] Build & Push
  ├─ Multi-stage Docker build
  ├─ Push to GHCR
  └─ Trivy image scan
    │
    ▼
[Job 4] Deploy → Staging
  ├─ kubectl apply
  └─ Smoke tests
    │
    ▼
[Job 5] Deploy → Production
  ├─ Blue-green deployment
  └─ Health verification
```

---

## ☸️ Kubernetes

```bash
# Deploy to cluster
make k8s-apply

# Check status
make k8s-status

# Rollback on failure
make k8s-rollback
```

**Features:**
- 3 app replicas with rolling updates (0 downtime)
- HPA: scales 2→10 pods on CPU/memory pressure
- Resource limits & requests on every container
- Non-root user, read-only filesystem
- Liveness + readiness probes
- Prometheus annotations for auto-discovery

---

## 📊 Monitoring

Prometheus collects metrics every 10s. Grafana dashboards include:

- Request rate per endpoint
- 95th percentile latency
- Error rate (4xx / 5xx)
- Book operations (create/update/delete)
- Active loans count

**Alert rules** fire when:
- App is down > 1 minute → **critical**
- Error rate > 5% for 2 minutes → **warning**
- P95 latency > 1s for 5 minutes → **warning**
- Database unreachable > 30s → **critical**

---

## 🧪 Testing

```bash
make test          # Run all tests with coverage
pytest tests/ -k "test_loan"   # Run specific tests
```

Test coverage includes:
- Health endpoints
- CRUD for books, members, loans
- Business rules (no copies, inactive member)
- Data integrity (duplicate ISBN/email)
- Loan return flow + availability restoration

---

## 🔐 Security

- Non-root Docker user
- Read-only container filesystem
- Nginx rate limiting (10 req/s per IP)
- Security headers (XSS, CSRF, content-type)
- Metrics endpoint restricted to internal network
- Secrets managed via Kubernetes Secrets (use Sealed Secrets in prod)
- Dependency vulnerability scanning in CI

---

## 📁 Project Structure

```
library-system/
├── app/
│   ├── __init__.py          # App factory, metrics
│   ├── models/models.py     # SQLAlchemy models
│   └── routes/
│       ├── books.py
│       ├── members.py
│       ├── loans.py
│       └── health.py
├── tests/
│   └── test_api.py          # Full test suite
├── k8s/
│   └── deployment.yaml      # K8s manifests
├── monitoring/
│   ├── prometheus.yml
│   └── alerts.yml
├── scripts/
│   └── seed_db.py
├── .github/workflows/
│   └── ci-cd.yml            # GitHub Actions pipeline
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full local stack
├── nginx.conf
├── Makefile                 # Developer commands
└── requirements.txt
```
