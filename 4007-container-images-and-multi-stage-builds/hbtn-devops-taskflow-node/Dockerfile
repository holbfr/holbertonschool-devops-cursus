# =============================================================================
# Production image for the TaskFlow API — the reference multi-stage build.
#
# If you are working through "Container Images & Multi-stage Builds": do not
# read this file until you have finished Task 4 and written your own
# Dockerfile.optimized. It is here so you can compare afterwards.
#
# Two stages:
#   builder  (node:20-slim)   installs *all* dependencies and runs lint + unit
#                             tests, so a broken app cannot produce an image.
#   runtime  (node:20-alpine) gets production dependencies and application
#                             source only — no devDependencies, no test files,
#                             no npm cache, and no root.
#
# Note what the builder does *not* run: the integration suite. Those tests need
# a live PostgreSQL, and a build that depends on a running database is a build
# that fails in CI for reasons that have nothing to do with the code. Run them
# against the started stack instead (`npm run test:integration`).
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 — builder
# -----------------------------------------------------------------------------
FROM node:20-slim AS builder

WORKDIR /app

# Manifests first, source later: this layer is the expensive one and it stays
# cached for as long as package.json and package-lock.json are untouched.
COPY package.json package-lock.json ./

# npm ci (not npm install) installs strictly from the lockfile and fails loudly
# when the lockfile and package.json disagree. Deterministic builds start here.
RUN npm ci

COPY src/ ./src/

# Quality gate. `npm test` is the unit scope: no database, safe inside a build.
# The test file is then dropped so it can never reach the runtime stage.
RUN npm run lint && npm test && rm -f src/*.test.js

# -----------------------------------------------------------------------------
# Stage 2 — runtime
# -----------------------------------------------------------------------------
FROM node:20-alpine

ENV NODE_ENV=production

WORKDIR /app

# A second, production-only install rather than copying the builder's
# node_modules: the tree is guaranteed free of devDependencies, and it is built
# against this image's own libc (alpine uses musl, the builder uses glibc).
#
# The trailing `find` is not cosmetic: npm 10 reifies the whole lockfile tree
# and then removes the dev packages, leaving behind empty scope directories
# (node_modules/@eslint, node_modules/@jest, ...). They weigh nothing but they
# make "is eslint in this image?" answer yes. Delete them so the runtime tree
# says exactly what it contains.
COPY package.json package-lock.json ./
RUN npm ci --only=production \
    && npm cache clean --force \
    && find node_modules -type d -empty -delete

# Only the application source crosses the stage boundary.
COPY --from=builder /app/src ./src/

# Create the unprivileged account *after* every step that needed root.
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

EXPOSE 3000

# Alpine ships no curl, but it obviously ships node, so the probe is written
# with what the image actually has. /health queries the database, so a passing
# probe means "process up AND database reachable", not just "port open".
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:3000/health', r => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "src/server.js"]
