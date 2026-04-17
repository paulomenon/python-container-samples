# OpenShift Deployment Guide

This folder contains OpenShift manifests for all 16 example applications. Each YAML file includes everything OpenShift needs to build images from source and deploy them — no pre-built images required.

## What's in Each YAML File

Every manifest includes these OpenShift resources:

| Resource | Purpose |
|---|---|
| **ImageStream** | Stores built container images in the internal registry |
| **BuildConfig** | Tells OpenShift to pull source code from GitHub and build with the Dockerfile |
| **Deployment** | Runs the container, auto-redeploys when a new build completes |
| **Service** | Internal networking (ClusterIP) |
| **Route** | Exposes the app to the outside world with a URL |

Multi-service apps (e.g. microservices, event-driven) include all of the above for each service, plus a Redis Deployment where needed.

---

## Option A: Deploy Using YAML Manifests (Recommended)

This uses the `BuildConfig` in each YAML to build images directly from the GitHub repo.

### Step 1: Log in and create a project

```bash
# OpenShift Local (CRC)
oc login -u developer -p developer https://api.crc.testing:6443

# Developer Sandbox — copy the login command from the web console
oc login --token=<your-token> --server=<your-server>

# Create a project
oc new-project python-samples
```

### Step 2: Apply the manifest

```bash
oc apply -f flask-web-api.yml
```

This creates the ImageStream, BuildConfig, Deployment, Service, and Route in one go.

### Step 3: Trigger the first build

The `ConfigChange` trigger in the BuildConfig will start a build automatically. If it doesn't, trigger it manually:

```bash
oc start-build flask-web-api
```

### Step 4: Watch the build

```bash
# List builds
oc get builds

# Stream build logs
oc logs -f build/flask-web-api-1
```

The build pulls source from `https://github.com/paulomenon/python-container-samples.git`, runs the Dockerfile from the app's folder, and pushes the image to the internal registry.

### Step 5: Check the deployment

```bash
# Wait for pods to be ready
oc get pods -w

# View all resources for the app
oc get all -l app=flask-web-api
```

### Step 6: Get the URL

```bash
oc get route flask-web-api
```

Open the URL in the `HOST/PORT` column in your browser.

### Rebuild after code changes

Push your changes to GitHub, then trigger a new build:

```bash
oc start-build flask-web-api
```

Or set up a webhook for automatic builds (see the BuildConfig webhook URL):

```bash
oc describe buildconfig flask-web-api | grep -A 5 "Webhook"
```

### Clean up

```bash
# Delete everything for one app
oc delete all -l app=flask-web-api
oc delete imagestream flask-web-api
oc delete buildconfig flask-web-api

# Delete the entire project
oc delete project python-samples
```

---

## Option B: Deploy Using S2I (Source-to-Image) — No YAML Needed

OpenShift can build and deploy directly from a Git repo in a single command using Source-to-Image. This skips the YAML files entirely — OpenShift detects the Python runtime and builds everything for you.

### Single command deploy

```bash
oc new-project python-samples

oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/flask-web-api \
    --name=flask-web-api
```

What this does:
- `python:3.12-ubi9` — the S2I builder image (Python 3.12 on Red Hat UBI)
- `~` — separates the builder image from the source repo
- `--context-dir` — which folder in the repo contains the app
- `--name` — the name for all created resources

### Expose the route

`oc new-app` does not create a Route by default — add one:

```bash
oc expose service flask-web-api
oc get route flask-web-api
```

### S2I commands for all starter examples

```bash
# Flask Web API
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/flask-web-api --name=flask-web-api
oc expose svc flask-web-api

# FastAPI Microservice
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/fastapi-microservice --name=fastapi-microservice
oc expose svc fastapi-microservice

# REST API JSON
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/rest-api-json --name=rest-api-json
oc expose svc rest-api-json

# Health Check Endpoint
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/health-check-endpoint --name=health-check-endpoint
oc expose svc health-check-endpoint

# Environment Variable Config App
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/env-config-app --name=env-config-app \
    -e APP_ENV=production -e APP_NAME=env-config-app
oc expose svc env-config-app
```

### S2I commands for intermediate examples

```bash
# URL Shortener API
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/url-shortener-api --name=url-shortener-api
oc expose svc url-shortener-api

# File Upload Service
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/file-upload-service --name=file-upload-service
oc expose svc file-upload-service

# Logging + Monitoring App
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/logging-monitoring-app --name=logging-monitoring-app
oc expose svc logging-monitoring-app
```

For apps that need **Redis**, deploy Redis first:

```bash
# Deploy Redis
oc new-app redis:7-alpine --name=redis

# Task Queue Worker (API)
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/task-queue-worker --name=task-queue-api \
    -e REDIS_URL=redis://redis:6379
oc expose svc task-queue-api

# Redis Cache Service
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/redis-cache-service --name=redis-cache-service \
    -e REDIS_URL=redis://redis:6379
oc expose svc redis-cache-service
```

### S2I commands for advanced examples

```bash
# --- Microservices App ---
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/microservices-app/user-service --name=user-service
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/microservices-app/order-service --name=order-service
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/microservices-app/api-gateway --name=api-gateway \
    -e SERVICE_USER_URL=http://user-service:5001 \
    -e SERVICE_ORDER_URL=http://order-service:5002
oc expose svc api-gateway

# --- API Gateway + Backends ---
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/api-gateway-backend/backend-users --name=backend-users
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/api-gateway-backend/backend-products --name=backend-products
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/api-gateway-backend/gateway --name=gateway \
    -e BACKEND_USERS_URL=http://backend-users:8001 \
    -e BACKEND_PRODUCTS_URL=http://backend-products:8002
oc expose svc gateway

# --- Event-Driven System ---
oc new-app redis:7-alpine --name=redis
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/event-driven-system/producer --name=producer \
    -e REDIS_URL=redis://redis:6379
oc expose svc producer
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/event-driven-system/consumer --name=consumer \
    -e REDIS_URL=redis://redis:6379

# --- Autoscaling API ---
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/autoscaling-api --name=autoscaling-api
oc expose svc autoscaling-api
oc autoscale deployment/autoscaling-api --min=1 --max=10 --cpu-percent=50

# --- Distributed Web Scraper ---
oc new-app redis:7-alpine --name=redis
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/distributed-web-scraper/coordinator --name=coordinator \
    -e REDIS_URL=redis://redis:6379
oc expose svc coordinator
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/distributed-web-scraper/worker --name=worker \
    -e REDIS_URL=redis://redis:6379

# --- Auth Service JWT ---
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/auth-service-jwt --name=auth-service-jwt
oc expose svc auth-service-jwt
```

---

## YAML vs S2I — Which to Use?

| | YAML Manifests (Option A) | S2I Command (Option B) |
|---|---|---|
| **Best for** | Reproducible, version-controlled deployments | Quick prototyping and one-off deploys |
| **Customization** | Full control — probes, env vars, scaling, volumes | Basic — add env vars with `-e`, limited config |
| **Build method** | Dockerfile (you control the build) | S2I builder (OpenShift chooses how to build) |
| **Multi-service** | Single YAML deploys everything together | Separate commands for each service |
| **GitOps friendly** | Yes — YAML files live in your repo | No — configuration lives in the cluster |
| **Rebuild** | `oc start-build <name>` | `oc start-build <name>` |

---

## Useful Commands

```bash
# View all resources in the project
oc get all

# View build logs
oc logs -f build/<build-name>

# View pod logs
oc logs -f deployment/<name>

# Scale a deployment
oc scale deployment/<name> --replicas=3

# Set an environment variable
oc set env deployment/<name> MY_VAR=my_value

# Open the web console
oc console

# Delete everything in the project
oc delete project python-samples
```
