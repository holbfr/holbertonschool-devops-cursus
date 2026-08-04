# TASK 0 Commands 

#### Build the image:
```
docker build -t flask-health-app .
```

#### Run the container:
```
docker run --rm -p 5000:5000 flask-health-app
```

#### Then access:
```
http://127.0.0.1:5000/
http://127.0.0.1:5000/health
http://127.0.0.1:5000/kill
```

---

# TASK 1 Commands


#### Start all services
```bash
docker compose up
```

#### Start all services in the background (detached mode)
```bash
docker compose up -d
```

#### Build (or rebuild) images before starting
```bash
docker compose up --build
```

#### Stop and remove containers, networks, and default resources
```bash
docker compose down
```

#### Stop and remove everything, including named volumes
⚠️ This deletes persistent data stored in named volumes.

```bash
docker compose down -v
```

#### List running services
```bash
docker compose ps
```

#### View logs from all services
```bash
docker compose logs
```

#### Follow (stream) logs from all services
```bash
docker compose logs -f
```

#### View logs from a specific service
```bash
docker compose logs backend1
```

#### Follow logs from a specific service
```bash
docker compose logs -f backend1
```

#### Execute a command inside a running container
```bash
docker compose exec backend1 sh
```

Example:

```bash
docker compose exec backend1 flask routes
```

#### Validate and display the fully resolved Compose configuration
```bash
docker compose config
```

#### Build images without starting containers
```bash
docker compose build
```

#### Start existing containers without rebuilding
```bash
docker compose start
```

#### Stop running containers without removing them
```bash
docker compose stop
```

#### Restart services
```bash
docker compose restart
```

---

# TASK 2 Commands



---
