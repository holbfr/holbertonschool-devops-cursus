## Load Balancing & Redundancy Lab

#### Introduction and context
* A load balancer is the single most important tool in the web DevOps toolbox. It turns a fragile single-server deployment into a resilient, scalable system — if configured correctly. In this project you will stand up a working load-balancer + backend cluster locally with Docker Compose, watch requests distribute across healthy backends, and verify that killing one backend does not break the service.

#### Learning and Objectives
By the end of this project, learners will be able to:

* Explain the difference between L4 and L7 load balancing.
* Configure Nginx or HAProxy as a reverse proxy with round-robin load balancing.
* Implement HTTP health checks and remove unhealthy backends from rotation.
* Observe traffic distribution with logs and metrics.
* Demonstrate failover behavior by taking a backend down.

---
---

## Explanations

---

#### What's a Load Balancer ?
- A **load balancer** is a device or software that **distributes incoming network traffic across multiple servers**.
- Its main goal is to prevent any single server from becoming overloaded.
- It improves:
  - **Availability** – If one server fails, traffic is redirected to healthy servers.
  - **Performance** – Distributes the workload, reducing response times.
  - **Scalability** – Makes it easy to add more servers as demand increases.
- Clients connect to the **load balancer**, which forwards each request to an appropriate backend server.

---

##### The difference between L4 and L7 load balancing.

##### L4 (Layer 4) Load Balancing

- Operates at the **Transport Layer (Layer 4)** of the OSI model.
- Routes traffic based on:
  - Source IP address
  - Destination IP address
  - Port number
  - Protocol (TCP/UDP)
- **Does not inspect the contents** of the data being transmitted.
- **Advantages:**
  - Very fast and efficient.
  - Low processing overhead.
  - Works with any TCP/UDP application.
- **Common use cases:**
  - Databases
  - SSH
  - Game servers
  - Generic TCP/UDP applications


##### L7 (Layer 7) Load Balancing

- Operates at the **Application Layer (Layer 7)** of the OSI model.
- Can inspect the contents of HTTP/HTTPS requests, including:
  - URL paths (e.g., `/api`, `/login`)
  - HTTP headers
  - Cookies
  - Hostnames (e.g., `api.example.com`)
- Can intelligently route requests based on their content.
- **Advantages:**
  - Flexible and intelligent routing.
  - Supports advanced features such as path-based and host-based routing.
  - Can integrate with authentication, caching, and security features.
- **Common use cases:**
  - Websites
  - REST APIs
  - Microservices

---

##### L4 vs L7 Load Balancing

| Feature | L4 Load Balancer | L7 Load Balancer |
|---------|------------------|------------------|
| **OSI Layer** | Layer 4 (Transport) | Layer 7 (Application) |
| **Routes Based On** | IP address, Port, Protocol | URL, Headers, Cookies, Hostname |
| **Inspects Request Content?** | ❌ No | ✅ Yes |
| **Performance** | Faster | Slightly slower (more processing) |
| **Routing** | Connection-based | Content-based |
| **Best For** | TCP/UDP services | Web applications and APIs |

---

# Quick Rule of Thumb

- ✅ **Choose L4** if you need **high performance** and only need to distribute TCP/UDP connections.
- ✅ **Choose L7** if you need **intelligent routing** based on HTTP/HTTPS request content.
More resources:
* Useful [youtube short](https://www.youtube.com/shorts/sOL64q1E9Bk)

---

#### What's a proxy?
- A **proxy** is a server that acts as an **intermediary between a client and another server**.
- Instead of connecting directly to the destination server, the client sends requests to the proxy.
- The proxy then forwards the request and returns the response to the client.
- **Common purposes:**
  - Hide the client's IP address.
  - Improve security by filtering requests.
  - Cache frequently accessed content to improve performance.
  - Restrict or monitor internet access.

---

#### What's a Reverse Proxy?
- A **reverse proxy** is a server that sits **in front of one or more backend servers**.
- Clients send requests to the reverse proxy, **without knowing which backend server handles the request**.
- The reverse proxy forwards each request to the appropriate backend server.
- **Common purposes:**
  - Load balancing across multiple servers.
  - Hide and protect backend servers.
  - Improve security (e.g., SSL termination, DDoS protection).
  - Cache responses to improve performance.

> **Difference:** A **proxy** represents the **client**, while a **reverse proxy** represents the **servers**.

---

#### What is Round Robin Load Balancing?

- **Round Robin** is one of the simplest load balancing algorithms.
- It distributes incoming requests **sequentially** across all available servers.
- Example with three servers:
  1. Request 1 → Server A
  2. Request 2 → Server B
  3. Request 3 → Server C
  4. Request 4 → Server A
  5. Request 5 → Server B
- **Advantages:**
  - Simple to implement.
  - Provides an even distribution when servers have similar capacity.
- **Limitation:**
  - Assumes all servers have the same performance and current workload.

---

#### What is Failover Behavior When a Server is Down?

- **Failover** is the process of **automatically redirecting traffic away from a failed server**.
- Load balancers regularly perform **health checks** to verify that backend servers are running correctly.
- If a server becomes unavailable:
  - The load balancer marks it as **unhealthy**.
  - New requests are sent only to the remaining healthy servers.
- When the failed server recovers:
  - The load balancer detects it through health checks.
  - The server is added back to the pool and starts receiving traffic again.
- **Benefits:**
  - Minimizes downtime.
  - Improves application reliability and availability.

---

## Quick Summary

| Concept | Purpose |
|---------|---------|
| **Proxy** | Represents the client when accessing another server. |
| **Reverse Proxy** | Represents backend servers and forwards client requests to them. |
| **Round Robin** | Distributes requests evenly across servers in a rotating order. |
| **Failover** | Automatically redirects traffic when a server becomes unavailable. |

