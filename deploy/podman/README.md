# Podman Deployment Guide

This folder contains Podman Compose files for all 16 example applications. Each `.yml` file defines the services, build context, ports, environment variables, and dependencies needed to run the app locally with Podman.

---

## Prerequisites

1. **Podman** installed and running:

```bash
podman machine init
podman machine start
podman --version
```

2. **Podman Compose** installed:

```bash
pip install podman-compose
```

---

## Deploying with Podman Desktop

Podman Desktop provides a graphical interface for managing containers.

1. Open **Podman Desktop**
2. Go to **Containers** → click **Create**
3. Select **From a Compose file** (or **Compose** in the sidebar)
4. Browse to this folder and select any `.yml` file (e.g. `flask-web-api.yml`)
5. Click **Start** — Podman Desktop will build the image and start the container
6. Once running, click the container to see logs, inspect ports, and open the app in your browser

To stop: click the **Stop** button next to the running container.

---

## Deploying with Podman CLI

### Build and Run a Single App (without Compose)

```bash
# Navigate to the app folder
cd apps/flask-web-api

# Build the image from the Containerfile
podman build -t flask-web-api .

# Run the container
podman run -d --name flask-web-api -p 5000:5000 flask-web-api
```

The `-d` flag runs the container in the background (detached mode).

### Build and Run with Podman Compose

```bash
# From the repo root, use the compose file
cd deploy/podman

# Start the app (builds the image if needed)
podman-compose -f flask-web-api.yml up -d

# Start with a fresh build (useful after code changes)
podman-compose -f flask-web-api.yml up -d --build
```

### Stop and Remove

```bash
# Stop a single container
podman stop flask-web-api

# Stop and remove with Compose
podman-compose -f flask-web-api.yml down

# Remove a named container
podman rm flask-web-api
```

---

## Changing the App Port

By default, each app exposes a specific port (most use `5000`, FastAPI-based apps use `8000`). You can change the **host port** (the port on your machine) without modifying the app itself.

### Option 1: Change port with `podman run`

```bash
# Map host port 9000 to container port 5000
podman run -d --name flask-web-api -p 9000:5000 flask-web-api
```

The format is `-p HOST_PORT:CONTAINER_PORT`. Now the app is available at `http://localhost:9000`.

### Option 2: Change port in the Compose file

Edit the `.yml` file and change the left side of the port mapping:

```yaml
services:
  flask-web-api:
    build: ../../apps/flask-web-api
    ports:
      - "9000:5000"    # was "5000:5000"
```

Then restart:

```bash
podman-compose -f flask-web-api.yml down
podman-compose -f flask-web-api.yml up -d
```

### Option 3: Run multiple instances on different ports

```bash
podman run -d --name flask-api-1 -p 5000:5000 flask-web-api
podman run -d --name flask-api-2 -p 5001:5000 flask-web-api
podman run -d --name flask-api-3 -p 5002:5000 flask-web-api
```

Now you have three instances running on ports 5000, 5001, and 5002.

---

## Checking if the App is Running

### List running containers

```bash
podman ps
```

Output:

```
CONTAINER ID  IMAGE               COMMAND     CREATED        STATUS        PORTS                   NAMES
a1b2c3d4e5f6  localhost/flask...   python ...  5 seconds ago  Up 5 seconds  0.0.0.0:5000->5000/tcp  flask-web-api
```

### List all containers (including stopped)

```bash
podman ps -a
```

### Check container logs

```bash
# Follow logs in real time
podman logs -f flask-web-api

# Show last 50 lines
podman logs --tail 50 flask-web-api
```

### Inspect a container

```bash
# Full container details (ports, env vars, mounts, etc.)
podman inspect flask-web-api

# Just the port mappings
podman port flask-web-api
```

### Check container resource usage

```bash
podman stats flask-web-api
```

---

## Testing the App

### curl — Test API Endpoints

Most apps expose REST APIs. Use `curl` to verify they work.

**Flask Web API (port 5000):**

```bash
curl http://localhost:5000
curl http://localhost:5000/api/items
```

**FastAPI Microservice (port 8000):**

```bash
curl http://localhost:8000
curl http://localhost:8000/docs    # opens Swagger UI in a browser
```

**Health Check Endpoint:**

```bash
curl http://localhost:5000/health
curl http://localhost:5000/ready
```

**REST API with JSON — CRUD operations:**

```bash
# Create
curl -X POST http://localhost:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "A test"}'

# Read all
curl http://localhost:5000/api/items

# Read one
curl http://localhost:5000/api/items/1

# Update
curl -X PUT http://localhost:5000/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item"}'

# Delete
curl -X DELETE http://localhost:5000/api/items/1
```

**URL Shortener:**

```bash
# Shorten a URL
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'

# Follow the short URL
curl -L http://localhost:5000/abc123
```

**Auth Service (JWT):**

```bash
# Register a user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret123"}'

# Login and get a token
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Access a protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/protected
```

**File Upload Service:**

```bash
# Upload a file
curl -X POST http://localhost:5000/upload \
  -F "file=@./README.md"

# List uploaded files
curl http://localhost:5000/files
```

### Quick health check with exit code

```bash
# Returns 0 if the app responds, non-zero if it fails
curl -sf http://localhost:5000/health > /dev/null && echo "UP" || echo "DOWN"
```

---

## Default Ports Reference

| Compose File | App Port | Services |
|---|---|---|
| `flask-web-api.yml` | 5000 | Flask API |
| `fastapi-microservice.yml` | 8000 | FastAPI |
| `rest-api-json.yml` | 5000 | REST API |
| `health-check-endpoint.yml` | 5000 | Health Check |
| `env-config-app.yml` | 5000 | Env Config |
| `url-shortener-api.yml` | 5000 | URL Shortener |
| `task-queue-worker.yml` | 5000, 6379 | API + Redis |
| `file-upload-service.yml` | 5000 | File Upload |
| `logging-monitoring-app.yml` | 5000 | Logging + Metrics |
| `redis-cache-service.yml` | 5000 | Cache API + Redis |
| `microservices-app.yml` | 5000, 5001, 5002 | Gateway + Users + Orders |
| `api-gateway-backend.yml` | 8000, 8001, 8002 | Gateway + Products + Users |
| `event-driven-system.yml` | 5000 | Producer + Consumer + Redis |
| `autoscaling-api.yml` | 8000 | Autoscaling API |
| `distributed-web-scraper.yml` | 5000 | Coordinator + Workers + Redis |
| `auth-service-jwt.yml` | 8000 | Auth Service |

---

## Troubleshooting

### Port already in use

```bash
# Find what's using port 5000
lsof -i :5000

# Kill it, or use a different host port
podman run -d --name flask-web-api -p 9000:5000 flask-web-api
```

### Container exits immediately

```bash
# Check the logs for errors
podman logs flask-web-api

# Run interactively to see output directly
podman run -it --name flask-web-api -p 5000:5000 flask-web-api
```

### Permission denied errors

```bash
# Run Podman in rootless mode (default on most systems)
podman info | grep rootless

# Ensure Podman machine is running
podman machine list
podman machine start
```

### Rebuild after code changes

```bash
# With Compose
podman-compose -f flask-web-api.yml up -d --build

# Without Compose
podman build -t flask-web-api --no-cache apps/flask-web-api/
podman stop flask-web-api && podman rm flask-web-api
podman run -d --name flask-web-api -p 5000:5000 flask-web-api
```

### Clean up everything

```bash
# Stop all containers
podman stop -a

# Remove all containers
podman rm -a

# Remove all images
podman rmi -a

# Full cleanup (containers, images, volumes, cache)
podman system prune -a
```
