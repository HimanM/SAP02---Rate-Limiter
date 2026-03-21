# SYSTEM-ARCHITECTURE-PROJECT-02 RateGuard - Distributed API Gateway with Rate Limiting

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Folder Structure](#folder-structure)
3. [Technology Stack](#technology-stack)
4. [Component Design Reasoning](#component-design-reasoning)
5. [Request Flow Logic](#request-flow-logic)
6. [Prerequisites & Output](#prerequisites--output)
7. [Deployment Guide](#deployment-guide)
8. [API Endpoints](#api-endpoints)

---

## System Architecture
The core philosophy revolves around enforcing scalable, distributed rate limits across multiple stateless gateway instances, utilizing a centralized in-memory datastore to track token metrics without blocking the critical request proxy path.

<figure style="max-width:800px; margin:0 0 12px 0;">
<pre>
Client
  ↓
NGINX (Load Balancer & Entrypoint)
  ↓
RateGuard Gateway Instances (Docker Replicas)
  ├─ Middleware: Token Bucket Rate Limiter
  └─ Forwarding Logic: Reverse Proxy to backend
  ↓
Redis (Shared state buffer)
  ↓
Backend Services (Docker Replicas)
</pre>
    <figcaption style="font-size:12px; color:#555;">Architecture diagram mapping the reverse proxy flow</figcaption>
</figure>

---

## Folder Structure
The repository is divided into discrete microservices ensuring separation of concerns:

```text
SAP02 - Rate Limiter/
├── rateguard/               # The core Python API Gateway & Middleware
│   ├── app.py               # Main Flask application and routing
│   ├── middleware.py        # Token Bucket algorithm and Redis state logic
│   ├── proxy.py             # Downstream request forwarding system
│   ├── config.py            # Environment configurations
│   └── Dockerfile           # Gateway containerization strategy
├── backend/                 # Simulated business logic servers
│   ├── app.py               # Mock API returning container replica hostnames
│   └── Dockerfile           # Backend containerization strategy
├── nginx/                   # Reverse proxy configuration
│   └── nginx.conf           # Load balancing strategy and Docker DNS resolution
├── tests/                   # Analytics and validation scripts
│   ├── burst_test.py        # Validates rate-limiter Token Bucket capacity
│   └── load_balance_test.py # Confirms NGINX round-robin functionality
├── docker-compose.yml       # Production-ready compose configuration
└── README.md                # System documentation
```

---

## Technology Stack

### Gateway & Backend 
* **Python (Flask)**: Extremely lightweight WSGI web application framework utilized for rapid HTTP intercept and reverse proxy processing.
* **Gunicorn**: Industrial-grade Python WSGI HTTP server executing the Flask applications in concurrent multi-worker environments to handle intense load operations.
* **Requests**: Standard HTTP library used for smoothly piping client payloads directly to backend endpoints.

### State & Routing
* **Redis**: Immensely fast in-memory key-value data store selected for its atomic operations, acting as the singular source of truth for rate limiting configurations and concurrent token calculations.
* **NGINX**: High-performance asynchronous edge proxy dynamically resolving Docker container DNS to automatically load balance client traffic across dynamically scaling gateway replicas.
* **Docker Compose**: Containerization module streamlining the infrastructure mapping, enabling flawless deployment using the internal Compose network and `deploy: replicas` replication factor logic.

---

## Component Design Reasoning
Every component within the infrastructure was carefully chosen to solve strict bottlenecks occurring at immense scale:

* **Token Bucket Algorithm**: RateGuard implements the classic token logic. A mathematical simulation calculates token regeneration (refill rate) against the timestamp of the preceding request. This elegantly enforces sustained limits while securely absorbing temporary traffic spikes (Burst Capacity).
* **Distributed Shared State**: Replicating gateway nodes natively causes local memory to fracture. To prevent users from circumventing throttling limits by routing to alternate containers, RateGuard actively utilizes **Redis** to synchronize global rate states uniformly across all localized nodes.
* **Atomic Concurrency Fix (Lua Scripts)**: When multiple concurrent requests (bursts) read a shared distributed state at the exact same millisecond, standard `GET`/`SET` calls induce a massive **Race Condition** giving false-positive approvals before tokens deduct. RateGuard mitigates this by abstracting the mathematical logic into an isolated, modular **Redis Lua Script** (`token_bucket.lua`). Redis automatically evaluates Lua logic atomically on a single thread—mathematically guaranteeing consistent throttling calculations while blocking concurrent collisions.
* **Fail-Open Design**: In distributed systems, partial failures shouldn't necessarily halt the entire application. The RateGuard middleware includes a **Fail-Open safety net**: if Redis goes offline, the gateway catches the exception and gracefully permits traffic (failing 'open' instead of crashing closed).
* **Container Replication & DNS Round-Robin**: Instead of explicitly hardcoding gateway nodes, the architecture leverages Docker's embedded `127.0.0.11` DNS resolver within the Nginx configuration natively. Pairing this with Docker Compose `deploy: replicas` horizontally scales the deployment flawlessly on demand.

---

## Request Flow Logic

### 1. Connection Intercept
External client communication initially establishes contact natively through the **NGINX Load Balancer**. Utilizing Docker DNS routing, traffic is smoothly injected asynchronously into a randomly selected **RateGuard Gateway Replica**.

### 2. Token Bucket Evaluation
Before the primary router acknowledges the path, the Flask `@before_request` middleware physically evaluates the user identity against the Redis node.
* It structurally parses the JSON state to check `remaining_tokens` and `last_refill` parameters.
* Based on the time delta since the prior interaction, it linearly recalculates new available tokens.
* If tokens `≥ 1`, it atomically deducts a token, saves the unified timestamp mapping to Redis, and signals approval. 
* If tokens `< 1`, the gateway immediately rejects the payload natively executing an `HTTP 429 Too Many Requests` denial response.

### 3. Downstream Forwarding
Successfully authorized interactions are handled organically by the internal proxy utility. The inbound headers, paths, and payloads are functionally rebuilt and transmitted downstream into the **Backend Cluster Replicas**. The generated backend response is ultimately captured and flushed chronologically back through the exact origin path sequentially.

---

## Prerequisites & Output
To execute the infrastructure mapping, your local environment requires:
* Docker Engine (v24.0 or newer)
* Docker Compose Module (v2.0 or newer)
* Port `8080` clear of localized bindings

---

## Deployment Guide
The entire structural framework actively provisions precisely out of the box dynamically leveraging Docker Compose.

1. Clone the repository framework locally.
2. Validate Docker Engine core variables.
3. Natively execute the container build script completely within the repository base:
   ```bash
   docker compose up --build -d
   ```
4. Access the unified backend API cleanly mapped via the edge proxy:
   `http://localhost:8080/api/info`

---

## API & Testing Diagnostics

### Burst Diagnostics
Simulates aggressive parallel concurrent requests natively testing the architectural burst limitations.
```bash
python tests/burst_test.py
```
*Outputs an optimized color-coded log physically marking exactly which threads legally claimed tokens versus which interactions were violently throttled.*

### Telemetry Load Balance Mapping
Generates linear, sequential requests analyzing how internal routing shifts the backend response nodes asynchronously.
```bash
python tests/load_balance_test.py
```
*Visually renders the distinct dynamic hostname variables returned by discrete Docker backend replicas, technically validating the networking flow distribution.*
