# Uber-inspired Microservices (Python) — Full Project Scaffold

This is a **full scaffold** for an Uber-like platform designed to demonstrate the *monolith → microservices* motivation:
independent deploys, bounded contexts, and event-driven communication.

**What you get now**
- Docker Compose for local dev: RabbitMQ + (optional) Postgres per service + all services
- A shared event-bus wrapper (aio-pika) + event types
- Event contracts (JSON Schema) + lightweight validation helper
- Service templates (FastAPI) for:
  - API Gateway (BFF)
  - Rider Service
  - Driver Service
  - Trip Service
  - Pricing Service
  - Payment Service
  - Notification Service
- Health endpoints, logging baseline, and a standard project layout
- GitHub Actions CI (lint + tests + docker build)
- Diagrams: C4 Container diagram and Trip Lifecycle sequence diagram
- Pre-commit config (format/lint)

**What is implemented vs stubbed**
- Trip + Driver include working event loop examples (publish/subscribe)
- The other services are stubbed with endpoints and TODO markers so we can build them together.

## Run (Docker)
```bash
docker compose up --build
```

### Useful URLs
- Gateway docs: http://localhost:3000/docs
- Trip docs: http://localhost:3003/docs
- Driver docs: http://localhost:3002/docs
- RabbitMQ UI: http://localhost:15672 (app/app)

## Diagrams
- [C4 Container Diagram](diagrams/c4_container.puml) - Overview of services, databases, and message queue
- [Trip Lifecycle Sequence Diagram](diagrams/trip_lifecycle.puml) - Event flow for a trip

## CI/CD
- GitHub Actions workflow for linting, testing, and building Docker images
- Pushes images to GitHub Container Registry on main branch
- Placeholder for deployment to VM

## Suggested learning path (what we’ll implement next)
1) Add Pricing service: `trip.requested` -> `pricing.quoted`
2) Add Payment service: `trip.completed` -> `payment.charged`
3) Add Notification service: consume events and send emails/logs
4) Add Rider service + auth-lite
5) Add Gateway orchestration endpoints for demo flow
6) Swap in-memory stores to Postgres (already in compose)
