# Advanced Examples

Real-world, production-style Python applications that demonstrate microservices architecture, event-driven systems, horizontal autoscaling, distributed computing, and authentication.

## Applications

| Folder | Example | Description |
|---|---|---|
| [`microservices-app/`](../microservices-app/) | Microservices App | Multiple Python services communicating via REST |
| [`api-gateway-backend/`](../api-gateway-backend/) | API Gateway + Backend Services | Gateway routing to backend microservices |
| [`event-driven-system/`](../event-driven-system/) | Event-driven System | Producer/consumer with Redis Pub/Sub |
| [`autoscaling-api/`](../autoscaling-api/) | Autoscaling API | CPU-intensive endpoint for HPA scaling demo |
| [`distributed-web-scraper/`](../distributed-web-scraper/) | Distributed Web Scraper | Coordinator + worker pattern for parallel scraping |
| [`auth-service-jwt/`](../auth-service-jwt/) | Authentication Service | JWT-based auth with login, register, and protected routes |

## What You'll Learn

- Microservices architecture with multiple containers
- API gateway pattern for routing and load balancing
- Event-driven communication with Redis Pub/Sub
- Horizontal Pod Autoscaler (HPA) configuration in Kubernetes
- Distributed task coordination (coordinator + worker pattern)
- JWT-based authentication and authorization
- Inter-service communication within a container network
- OpenShift BuildConfig and ImageStream for source-to-image builds

## Getting Started

Advanced examples typically involve multiple services. Use Podman Compose to bring everything up at once:

```bash
cd deploy/podman
podman-compose -f microservices-app.yml up
```

For OpenShift with source builds:

```bash
oc apply -f deploy/openshift/microservices-app.yml
oc start-build microservices-app-users
oc start-build microservices-app-orders
oc start-build microservices-app-gateway
```

For Kubernetes:

```bash
# Build all service images
podman build -t microservices-gateway:latest apps/microservices-app/gateway/
podman build -t microservices-users:latest apps/microservices-app/users-service/
podman build -t microservices-orders:latest apps/microservices-app/orders-service/

# Load into Kind cluster
kind load docker-image microservices-gateway:latest --name python-samples
kind load docker-image microservices-users:latest --name python-samples
kind load docker-image microservices-orders:latest --name python-samples

kubectl apply -f deploy/kubernetes/microservices-app.yml
```

See the [main README](../../README.md) for full platform setup instructions.
