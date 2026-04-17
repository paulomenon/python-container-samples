# Ansible Playbooks for Kubernetes & OpenShift

A collection of Ansible playbooks that automate common Kubernetes and OpenShift infrastructure tasks — from namespace provisioning to RBAC setup to multi-environment deployments.

## Playbooks

| Playbook | What It Does |
|---|---|
| `namespace-auto-provisioning.yml` | Creates namespaces with labels, resource quotas, and limit ranges |
| `configmap-secret-generator.yml` | Reads `.env` files and creates ConfigMaps and Secrets (auto-classifies sensitive keys) |
| `pod-resource-validator.yml` | Scans running pods and reports missing resource limits/requests or threshold violations |
| `yaml-manifest-validator.yml` | Validates YAML syntax, checks for deprecated APIs, runs `kubectl --dry-run` |
| `multi-env-deployment-generator.yml` | Generates Deployment, Service, and ConfigMap manifests for dev/staging/prod |
| `rbac-generator.yml` | Creates ServiceAccounts, Roles, and RoleBindings (readonly, deployer, admin, monitoring) |
| `ingress-rule-builder.yml` | Builds Kubernetes Ingress or OpenShift Route resources for multi-service routing |

---

## Prerequisites

### 1. Install Ansible

```bash
# macOS
brew install ansible

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ansible

# pip (any platform)
pip install ansible
```

### 2. Install the Kubernetes Ansible Collection

Most playbooks use the `kubernetes.core` collection to interact with the cluster:

```bash
ansible-galaxy collection install kubernetes.core
```

### 3. Install the Python Kubernetes Client

Ansible's Kubernetes modules rely on the Python `kubernetes` library:

```bash
pip install kubernetes openshift
```

### 4. Authenticate to Your Cluster

**Kubernetes:**

```bash
# Ensure kubectl can reach your cluster
kubectl cluster-info
kubectl get nodes
```

**OpenShift:**

```bash
# Log in with the oc CLI
oc login -u developer -p developer https://api.crc.testing:6443

# Or use a token from the web console
oc login --token=<your-token> --server=https://api.your-cluster.com:6443
```

Ansible uses your current `~/.kube/config` context, so if `kubectl` or `oc` works, Ansible will too.

---

## Running Playbooks on Kubernetes

```bash
cd ansible

# Create namespaces (dev, staging, prod) with quotas and limits
ansible-playbook namespace-auto-provisioning.yml -e "target_platform=kubernetes"

# Generate ConfigMap and Secret from an env file
ansible-playbook configmap-secret-generator.yml -e "env_file=../apps/env-config-app/.env namespace=dev app_name=env-config-app"

# Check all pods for missing resource limits
ansible-playbook pod-resource-validator.yml

# Check pods in a specific namespace with custom thresholds
ansible-playbook pod-resource-validator.yml -e "target_namespace=prod max_cpu=2 max_memory_gi=4"

# Validate Kubernetes manifests
ansible-playbook yaml-manifest-validator.yml -e "manifest_dir=../deploy/kubernetes"

# Validate in strict mode (fails on any issue)
ansible-playbook yaml-manifest-validator.yml -e "manifest_dir=../deploy/kubernetes strict=true"

# Generate dev/staging/prod manifests
ansible-playbook multi-env-deployment-generator.yml -e "app_name=flask-web-api image=flask-web-api:latest"

# Set up RBAC roles
ansible-playbook rbac-generator.yml -e "namespace=dev"

# Build Kubernetes Ingress rules
ansible-playbook ingress-rule-builder.yml -e "target_platform=kubernetes domain=apps.example.com"
```

### Deploy the generated manifests

```bash
# After running multi-env-deployment-generator.yml:
kubectl apply -f generated-manifests/dev/
kubectl apply -f generated-manifests/staging/
kubectl apply -f generated-manifests/prod/
```

---

## Running Playbooks on OpenShift

The same playbooks work on OpenShift — just pass `target_platform=openshift`:

```bash
cd ansible

# Create OpenShift Projects (namespaces) with quotas
ansible-playbook namespace-auto-provisioning.yml -e "target_platform=openshift"

# Generate ConfigMap and Secret
ansible-playbook configmap-secret-generator.yml -e "env_file=../.env namespace=myproject app_name=myapp"

# Validate OpenShift manifests
ansible-playbook yaml-manifest-validator.yml -e "manifest_dir=../deploy/openshift"

# Set up RBAC with OpenShift ClusterRole bindings
ansible-playbook rbac-generator.yml -e "namespace=dev target_platform=openshift"

# Build OpenShift Routes instead of Ingress
ansible-playbook ingress-rule-builder.yml -e "target_platform=openshift domain=apps.ocp.example.com"
```

### OpenShift-specific features

- **Namespace → Project**: The namespace playbook creates OpenShift `Project` resources instead of `Namespace`
- **RBAC**: Adds bindings to OpenShift built-in ClusterRoles (`view`, `edit`, `admin`)
- **Routes**: The ingress builder creates OpenShift `Route` resources with edge TLS termination instead of Kubernetes `Ingress`

---

## How Ansible Works Behind the Scenes

Ansible playbooks look like YAML, but **behind the scenes, every module is a Python script**.

When you run a playbook:

1. Ansible reads the YAML and determines which **modules** to execute
2. Each module (e.g. `kubernetes.core.k8s`) is a **Python script** that lives in `~/.ansible/collections/`
3. Ansible generates a Python script with the module code + your parameters
4. The script runs on the target (localhost for Kubernetes tasks)
5. The module calls the **Kubernetes Python client** (`kubernetes` pip package) to talk to the API server
6. Results come back as JSON, and Ansible handles success/failure/change tracking

For example, when you write:

```yaml
- name: Create namespace
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Namespace
      metadata:
        name: dev
```

Ansible translates this into roughly:

```python
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()

namespace = client.V1Namespace(
    metadata=client.V1ObjectMeta(name="dev")
)
v1.create_namespace(body=namespace)
```

The difference is that Ansible adds **idempotency** (it checks if the namespace already exists before creating), **error handling**, **change tracking**, and **logging** — all for free.

---

## Why Ansible Over Pure Python for Infrastructure

### The problem with Python scripts for infrastructure

A Python script to create a namespace might look simple:

```python
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()
v1.create_namespace(body=client.V1Namespace(metadata=client.V1ObjectMeta(name="dev")))
```

But in production, you'd also need to:
- Check if the namespace already exists (idempotency)
- Handle API errors and retries
- Log what changed and what didn't
- Support dry-run mode
- Manage credentials securely
- Handle rollbacks on failure
- Report results in a structured way

That's hundreds of lines of boilerplate that Ansible gives you out of the box.

### Side-by-side comparison

| Concern | Python Script | Ansible Playbook |
|---|---|---|
| **Idempotency** | You write it yourself (`try/except`, check-before-create) | Built-in — `state: present` handles it |
| **Error handling** | Manual `try/except` around every API call | Automatic — retries, `ignore_errors`, `failed_when` |
| **Change tracking** | You print messages manually | Built-in — "changed", "ok", "failed" per task |
| **Dry run** | You implement a `--dry-run` flag yourself | Built-in — `--check` mode |
| **Secrets** | Hardcoded or custom env loading | Ansible Vault encrypts secrets at rest |
| **Logging** | You build your own logger | Built-in — verbose modes (`-v`, `-vv`, `-vvv`) |
| **Rollback** | You write rollback logic | `block/rescue/always` handles it declaratively |
| **Reusability** | Functions, classes, imports | Roles, collections, variables |
| **Multi-environment** | Command-line args or config files | Inventory + group_vars per environment |
| **Readability** | Code — requires Python knowledge | YAML — readable by anyone on the team |

### When the difference matters most

**Creating 3 namespaces with quotas and limits:**

- **Python**: ~150 lines (API calls, error handling, idempotency checks, logging)
- **Ansible**: ~50 lines of YAML (declarative, idempotent by default)

**Setting up RBAC for 4 roles across 3 namespaces:**

- **Python**: ~300 lines (12 ServiceAccounts, 12 Roles, 12 RoleBindings, each with error handling)
- **Ansible**: ~80 lines of YAML with loops

---

## When to Use Python vs Ansible

### Simple Rule of Thumb

If your task includes words like:

- **"calculate"**
- **"validate"**
- **"transform"**
- **"compare"**

Use **Python**.

If it includes:

- **"deploy"**
- **"create"**
- **"configure"**
- **"ensure exists"**

Use **Ansible**.

### Detailed decision guide

| Task | Best Tool | Why |
|---|---|---|
| Parse a CSV and generate reports | **Python** | Data transformation, logic-heavy |
| Create 10 namespaces with quotas | **Ansible** | Infrastructure provisioning, idempotent |
| Validate JSON schema of API responses | **Python** | Validation, comparison logic |
| Deploy a microservices stack | **Ansible** | Multi-step deployment, state management |
| Analyze pod metrics and alert on anomalies | **Python** | Math, data analysis, custom logic |
| Configure RBAC roles across environments | **Ansible** | Declarative configuration, repeatability |
| Build a custom CLI tool | **Python** | Application logic, user interaction |
| Ensure Redis, app, and worker are running | **Ansible** | "Ensure exists" — perfect for desired-state |
| Compare two Kubernetes clusters for drift | **Python** | Deep comparison, custom diff logic |
| Set up Ingress routing for 10 services | **Ansible** | Infrastructure routing, declarative |
| Scrape websites and store results | **Python** | HTTP requests, parsing, data storage |
| Rotate secrets across all namespaces | **Ansible** | Secret management, idempotent updates |

### The sweet spot: use both together

Some playbooks in this collection combine both — for example, `pod-resource-validator.yml` uses Ansible to **query the cluster** and Python-style Jinja2 logic to **analyze the results**. This is the best of both worlds:

- Ansible handles the infrastructure interaction (auth, API calls, retries)
- Jinja2/filters handle the validation logic (comparisons, filtering, formatting)

---

## Folder Structure

```
ansible/
├── README.md
├── namespace-auto-provisioning.yml
├── configmap-secret-generator.yml
├── pod-resource-validator.yml
├── yaml-manifest-validator.yml
├── multi-env-deployment-generator.yml
├── rbac-generator.yml
├── ingress-rule-builder.yml
└── tasks/
    └── check-pod-resources.yml
```

---

## Useful Commands

```bash
# Run with verbose output
ansible-playbook playbook.yml -v

# Extra verbose (shows API calls)
ansible-playbook playbook.yml -vvv

# Dry run (check mode — no changes made)
ansible-playbook playbook.yml --check

# Override any variable
ansible-playbook playbook.yml -e "namespace=myns app_name=myapp"

# List all tasks without running them
ansible-playbook playbook.yml --list-tasks
```
