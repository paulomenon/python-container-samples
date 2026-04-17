# Python Container Samples

A collection of containerized Python applications — from simple Flask APIs to distributed microservices — with ready-to-use deployment configurations for **Podman**, **OpenShift**, and **Kubernetes**.

## Examples

| Level | Examples | Description |
|---|---|---|
| [**Starter**](apps/starter/) | 5 apps | Flask API, FastAPI, REST API, Health Checks, Env Config |
| [**Intermediate**](apps/intermediate/) | 5 apps | URL Shortener, Task Queue, File Upload, Logging, Redis Cache |
| [**Advanced**](apps/advanced/) | 6 apps | Microservices, API Gateway, Event-driven, Autoscaling, Scraper, JWT Auth |

See each level's README for the full list and details.

## Project Structure

```
python_container_samples/
├── apps/                      # All Python applications
│   ├── starter/README.md      # Starter examples overview
│   ├── intermediate/README.md # Intermediate examples overview
│   ├── advanced/README.md     # Advanced examples overview
│   ├── flask-web-api/         # Each app has its own folder with:
│   │   ├── app.py             #   - Python source code
│   │   ├── requirements.txt   #   - Dependencies
│   │   └── Containerfile      #   - Container build file
│   └── ...
├── deploy/                    # Deployment configurations
│   ├── podman/                #   - Podman Compose files
│   ├── openshift/             #   - OpenShift manifests + deployment guide
│   └── kubernetes/            #   - Kubernetes YAML manifests
└── README.md
```

---

## Prerequisites & Platform Setup

### Base Python Image

All examples use the official Python slim image as the base:

```
FROM python:3.12-slim
```

This keeps container images small (~150MB) while including everything Python needs.

---

## 1. Podman Desktop (Local Containers)

### What is Podman?

Podman is a daemonless container engine that runs containers without root privileges. It is OCI-compliant and works with standard Containerfiles.

### Install Podman Desktop

| Platform | Install |
|---|---|
| **macOS** | `brew install podman-desktop` or download from [podman-desktop.io](https://podman-desktop.io) |
| **Windows** | Download installer from [podman-desktop.io](https://podman-desktop.io) |
| **Linux** | `flatpak install io.podman_desktop.PodmanDesktop` or use your package manager |

After installing, open Podman Desktop and initialize a Podman machine:

```bash
podman machine init
podman machine start
```

Verify it works:

```bash
podman --version
podman run hello-world
```

### Running an Example with Podman

**Option A: Build and run a single container**

```bash
cd apps/flask-web-api
podman build -t flask-web-api .
podman run -p 5000:5000 flask-web-api
```

Open http://localhost:5000 in your browser.

**Option B: Use Podman Compose (for multi-container apps)**

```bash
pip install podman-compose    # if not already installed
cd deploy/podman
podman-compose -f flask-web-api.yml up
```

**Stop and clean up:**

```bash
podman-compose -f flask-web-api.yml down
podman system prune           # remove unused images/containers
```

---

## 2. OpenShift (Enterprise Kubernetes)

### What is OpenShift?

OpenShift is Red Hat's Kubernetes distribution with built-in CI/CD, a web console, and developer-friendly features like Source-to-Image (S2I) builds.

### Get a Local OpenShift Cluster

**Option A: OpenShift Local (CRC) — recommended for development**

1. Download from [developers.redhat.com/products/openshift-local](https://developers.redhat.com/products/openshift-local/overview)
2. Set up and start:

```bash
crc setup
crc start
```

3. Log in:

```bash
eval $(crc oc-env)
oc login -u developer -p developer https://api.crc.testing:6443
```

**Option B: Free OpenShift Online (Developer Sandbox)**

1. Go to [developers.redhat.com/developer-sandbox](https://developers.redhat.com/developer-sandbox)
2. Sign up with a Red Hat account (free)
3. You get a free OpenShift namespace for 30 days (renewable)
4. Log in with the provided `oc login` command from the web console

### Prerequisites

```bash
# Install the OpenShift CLI
brew install openshift-cli        # macOS
# or download from https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/
```

Verify:

```bash
oc version
oc whoami
```

### Deploying an Example to OpenShift

See the full [OpenShift Deployment Guide](deploy/openshift/README.md) for YAML-based and S2I deployment instructions.

**Quick start with S2I (no Containerfile needed):**

```bash
oc new-project python-samples
oc new-app python:3.12-ubi9~https://github.com/paulomenon/python-container-samples.git \
    --context-dir=apps/flask-web-api \
    --name=flask-web-api
oc expose service flask-web-api
oc get route flask-web-api
```

**Quick start with YAML manifests:**

```bash
oc apply -f deploy/openshift/flask-web-api.yml
oc start-build flask-web-api
oc get route flask-web-api
```

---

## 3. Kubernetes (K8s)

### What is Kubernetes?

Kubernetes is the industry-standard container orchestration platform. It manages container deployment, scaling, and networking.

### Run Kubernetes Locally

**Option A: Podman + Kind (Kubernetes in a container)**

```bash
# Install kind
brew install kind               # macOS
# or: go install sigs.k8s.io/kind@latest

# Create a cluster using Podman as the runtime
KIND_EXPERIMENTAL_PROVIDER=podman kind create cluster --name python-samples
```

**Option B: Minikube with Podman driver**

```bash
brew install minikube            # macOS
minikube start --driver=podman
```

### Free Cloud Kubernetes (No Credit Card)

| Provider | What you get | Link |
|---|---|---|
| **Google Cloud** | $300 free credits for 90 days (GKE) | [cloud.google.com/free](https://cloud.google.com/free) |
| **Oracle Cloud** | Always-free tier with 4 ARM Ampere A1 cores | [oracle.com/cloud/free](https://www.oracle.com/cloud/free/) |
| **Civo** | $250 free credit for 1 month | [civo.com](https://www.civo.com/) |
| **Red Hat Sandbox** | Free OpenShift namespace (K8s compatible) | [developers.redhat.com/developer-sandbox](https://developers.redhat.com/developer-sandbox) |

### Prerequisites

```bash
# Install kubectl
brew install kubectl             # macOS
# or download from https://kubernetes.io/docs/tasks/tools/

kubectl version --client
```

### Deploying an Example to Kubernetes

```bash
# Build the image and load it into the cluster
podman build -t flask-web-api:latest apps/flask-web-api/
kind load docker-image flask-web-api:latest --name python-samples

# Apply the Kubernetes manifests
kubectl apply -f deploy/kubernetes/flask-web-api.yml

# Check status
kubectl get pods
kubectl get services

# Access the app
kubectl port-forward service/flask-web-api 5000:5000
```

Open http://localhost:5000.

**Clean up:**

```bash
kubectl delete -f deploy/kubernetes/flask-web-api.yml
kind delete cluster --name python-samples
```

---

## Quick Reference

| Task | Podman | OpenShift | Kubernetes |
|---|---|---|---|
| Build image | `podman build -t name .` | `oc new-app` (S2I) | `podman build` + `kind load` |
| Run locally | `podman run -p 5000:5000 name` | — | `kubectl port-forward` |
| Deploy | `podman-compose up` | `oc apply -f file.yml` | `kubectl apply -f file.yml` |
| View logs | `podman logs container` | `oc logs pod` | `kubectl logs pod` |
| Scale | — | `oc scale --replicas=3` | `kubectl scale --replicas=3` |
| Clean up | `podman system prune` | `oc delete all -l app=name` | `kubectl delete -f file.yml` |

## License

MIT
