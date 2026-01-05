# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Uber-like microservices system.

## Prerequisites

- Kubernetes cluster (e.g., minikube, kind, or cloud)
- kubectl configured
- Docker images built and available (or pushed to registry)

## Building Images

First, build the Docker images:

```bash
docker build -t uberproject-gateway:latest services/gateway/
docker build -t uberproject-rider:latest services/rider_service/
docker build -t uberproject-driver:latest services/driver_service/
docker build -t uberproject-trip:latest services/trip_service/
docker build -t uberproject-pricing:latest services/pricing_service/
docker build -t uberproject-payment:latest services/payment_service/
docker build -t uberproject-notification:latest services/notification_service/
```

For local clusters like kind, load images:

```bash
kind load docker-image uberproject-gateway:latest
# ... repeat for others
```

## Deployment

Apply all manifests:

```bash
kubectl apply -f k8s/
```

Or individually:

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/mongodb.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/rabbitmq.yaml
kubectl apply -f k8s/rider.yaml
kubectl apply -f k8s/driver.yaml
kubectl apply -f k8s/trip.yaml
kubectl apply -f k8s/pricing.yaml
kubectl apply -f k8s/payment.yaml
kubectl apply -f k8s/notification.yaml
kubectl apply -f k8s/gateway.yaml
kubectl apply -f k8s/ingress.yaml
```

## Access

- Gateway: http://localhost:3000 (if using port-forward or ingress)
- RabbitMQ Management: kubectl port-forward svc/rabbitmq 15672:15672

## Cleanup

```bash
kubectl delete -f k8s/
```