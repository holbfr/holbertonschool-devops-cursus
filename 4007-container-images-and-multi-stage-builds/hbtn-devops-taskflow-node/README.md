# TaskFlow API — starter application

A deliberately small Express + PostgreSQL service. It exists to be
containerized, orchestrated, scaled and load-balanced — not to be impressive.
Three items in a table and three HTTP endpoints are enough to make every
infrastructure concept in the curriculum visible.

> **This is a teaching asset.** Several projects clone this repository and each
> uses a different subset of it. Some of what looks wrong here is wrong on
> purpose — see [Deliberate gaps](#deliberate-gaps) before you "fix" anything.

---

## API contract

The application listens on port **3000** inside its container, everywhere, in
every project.

| Method | Path      | Success            | Body / notes |
|--------|-----------|--------------------|--------------|
| `GET`  | `/health` | **200**            | `{"status":"ok","uptime":37.2,"hostname":"9f4c1ab73d20","database":"connected"}` |
| `GET`  | `/health` | **503**            | `{"status":"error",...,"database":"disconnected"}` when the database is unreachable |
| `GET`  | `/items`  | **200**            | the rows, ordered by `id` |
| `POST` | `/items`  | **201**            | `{"name":"..."}` in, the created row out |
| `POST` | `/items`  | **400**            | when `name` is missing or empty |

Two details matter more than they look:

- **`/health` queries the database.** It runs `SELECT 1` before answering, so a
  passing health check means "the process is up **and** its database connection
  works" — a far stronger signal than a TCP probe on port 3000. That is also why
  it can answer 503 while the process is perfectly alive.
- **`hostname` is `os.hostname()`**, which inside Docker is the container ID. It
  therefore differs per container, which is exactly what makes it usable as an
  instance marker once several replicas sit behind a load balancer.

The application never crashes because the database is missing. `pg.Pool`
connects lazily, so the HTTP server comes up immediately and `/health` reports
503 until Postgres is ready. Nothing needs restarting when the database
finally answers.

---

## Layout

```
.
├── src/
│   ├── server.js          the whole application
│   └── server.test.js     unit + integration suites (see Tests)
├── db/
│   ├── 01-schema.sql      CREATE TABLE items (...)
│   └── 02-seed.sql        exactly 3 rows: Alpha Task, Beta Task, Gamma Task
├── nginx/
│   └── nginx.conf         SKELETON — two TODOs to complete
├── Dockerfile             production multi-stage image
├── Dockerfile.baseline    intentionally bloated image
├── docker-compose.yml     baseline stack: db + app
├── package.json
└── package-lock.json
```

The `db/` scripts are mounted into the Postgres container's
`/docker-entrypoint-initdb.d`. The official image runs everything it finds
there **in filename-sorted order** and **only when the data directory is
empty** — that is what the `01-` / `02-` prefixes are for, and why the seed data
comes back after `docker compose down -v` but not after a plain
`docker compose down`.

---

## Run it

```bash
docker compose up -d --wait

curl -s http://localhost:3000/health | jq .
curl -s http://localhost:3000/items  | jq .
curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"name":"Delta Task"}' http://localhost:3000/items | jq .

docker compose down -v
```

`--wait` blocks until every service reports healthy, so a clean cold start
either succeeds or fails visibly.

### Without Docker

Any PostgreSQL will do; point the environment variables at it and load the two
SQL files in order.

```bash
npm ci
psql -d taskflow -f db/01-schema.sql
psql -d taskflow -f db/02-seed.sql
PGHOST=localhost PGDATABASE=taskflow npm start
```

---

## Configuration

Every connection detail comes from the environment. Nothing is hardcoded and
nothing is read from a file — which is what lets the same image run unchanged
in every stack you will build around it.

| Variable     | Default        | Notes |
|--------------|----------------|-------|
| `PGHOST`     | `localhost`    | in Compose this is the **service name** of the database, not `localhost` and not an IP |
| `PGPORT`     | `5432`         | |
| `PGUSER`     | `taskflow`     | |
| `PGPASSWORD` | `taskflow_dev` | development value; real deployments inject a real secret |
| `PGDATABASE` | `taskflow`     | |
| `PORT`       | `3000`         | the API's own listening port |

---

## Tests

Two scopes live in `src/server.test.js`, and the difference is the point:

| Command | Scope | Needs Postgres? |
|---|---|---|
| `npm test` | unit | no |
| `npm run test:unit` | unit — pure functions, config resolution, payload validation | no |
| `npm run test:integration` | integration — real HTTP requests, real rows | **yes** |
| `npm run lint` | eslint | no |

`npm test` runs the unit scope on purpose. A build must never depend on a
database being reachable, so that is the suite the `Dockerfile`'s builder stage
runs as its quality gate. The integration suite is for a **live stack**:

```bash
docker compose up -d --wait
PGHOST=localhost npm run test:integration          # in-process app, live db
BASE_URL=http://localhost:3000 npm run test:integration   # against the running container
```

It asserts the contract above: `/health` reports ok, `/items` returns the three
seed rows in id order, `POST /items` answers 201 with the created row, and a
POST without a name answers 400.

---

## Deliberate gaps

Do not "fix" these. Each one is somebody's assignment.

| What looks wrong | Why it is there |
|---|---|
| `Dockerfile.baseline` is enormous and runs as root | It is the measured starting point for the image-optimization project. Its header comments list every sin. |
| There is **no `.dockerignore`** | Writing it is a task. That is also why the build context is embarrassing until someone does. |
| `nginx/nginx.conf` does not work as shipped | It is a skeleton. Two `# TODO` markers cover the `upstream` block and the `proxy_pass` — the load-balancing lab's actual objective. The surrounding structure and the forwarding headers are given because nginx syntax is not what is being assessed. |
| `docker-compose.yml` publishes the app on host port 3000 | Convenient now, wrong later. Removing that mapping — so a proxy or load balancer becomes the only entry point — is a step in two different projects. |
| Credentials are literals in `docker-compose.yml` | Moving them to a gitignored `.env` with a committed `.env.example` is a task. |
| No SIGTERM handler in `src/server.js` | Graceful shutdown and connection draining are an extension exercise. |
| `Dockerfile` is a finished, production-grade multi-stage build | It is the reference solution. If you are working through the image-optimization project, do not open it until you have written your own. |

---

## License

MIT. Sample data and credentials are fictitious; never reuse them anywhere real.
