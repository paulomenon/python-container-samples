# Starter Examples

Simple, single-container Python applications to get comfortable with building and running containers using Podman, OpenShift, or Kubernetes.

## Applications

| Folder | Example | Description |
|---|---|---|
| [`flask-web-api/`](../flask-web-api/) | Simple Flask Web API | Basic REST API built with Flask |
| [`fastapi-microservice/`](../fastapi-microservice/) | FastAPI Microservice | Async API with FastAPI and auto-generated docs |
| [`rest-api-json/`](../rest-api-json/) | REST API with JSON Responses | CRUD operations returning JSON |
| [`health-check-endpoint/`](../health-check-endpoint/) | Health Check Endpoint | App with `/health` and `/ready` endpoints for container orchestration |
| [`env-config-app/`](../env-config-app/) | Environment Variable Config App | App configured entirely via environment variables |

## What You'll Learn

- Writing a `Containerfile` for a Python web app
- Building images with `podman build`
- Running containers with `podman run`
- Exposing ports and mapping them to your host
- Using Podman Compose to manage single-service apps
- Deploying to OpenShift and Kubernetes using YAML manifests

## Getting Started

Pick any example and run it locally:

```bash
cd apps/flask-web-api
podman build -t flask-web-api .
podman run -p 5000:5000 flask-web-api
```

Or use Podman Compose:

```bash
cd deploy/podman
podman-compose -f flask-web-api.yml up
```

See the [main README](../../README.md) for full platform setup instructions.
