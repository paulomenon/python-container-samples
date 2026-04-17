# Intermediate Examples

Cloud-native and DevOps-style Python applications that introduce multi-container setups, background workers, persistent storage, and observability.

## Applications

| Folder | Example | Description |
|---|---|---|
| [`url-shortener-api/`](../url-shortener-api/) | URL Shortener API | Shorten URLs with SQLite persistence |
| [`task-queue-worker/`](../task-queue-worker/) | Task Queue Worker | Background job processing with Redis + RQ |
| [`file-upload-service/`](../file-upload-service/) | File Upload Service | Upload and retrieve files via API |
| [`logging-monitoring-app/`](../logging-monitoring-app/) | Logging + Monitoring Demo | Structured logging with Prometheus metrics |
| [`redis-cache-service/`](../redis-cache-service/) | Redis-backed Cache Service | API with Redis caching layer |

## What You'll Learn

- Multi-container deployments with Podman Compose
- Using Redis as a message broker and cache
- Background job processing with RQ workers
- File upload handling and volume mounts
- Prometheus metrics endpoint for monitoring
- SQLite persistence in containers
- ConfigMaps and PersistentVolumeClaims in Kubernetes
- Service-to-service networking within a pod network

## Getting Started

Most intermediate examples require Redis or persistent storage. Use Podman Compose for the simplest setup:

```bash
cd deploy/podman
podman-compose -f task-queue-worker.yml up
```

For Kubernetes:

```bash
podman build -t task-queue-worker:latest apps/task-queue-worker/
kind load docker-image task-queue-worker:latest --name python-samples
kubectl apply -f deploy/kubernetes/task-queue-worker.yml
```

See the [main README](../../README.md) for full platform setup instructions.
