#
# Render deployment image: NestJS API (Node) + Python agent.
# The server spawns Python to run the agent (`python -m repo_risk_radar ...`),
# so both runtimes must exist in the same container.
#

FROM node:20-bookworm AS builder

WORKDIR /app

# Install Node deps for the monorepo (includes dev deps for TS build).
COPY package.json package-lock.json turbo.json ./
COPY apps/server/package.json apps/server/package.json
COPY apps/client/package.json apps/client/package.json

RUN npm ci

# Copy source after deps for better caching.
COPY apps/server apps/server

# Build the NestJS server (outputs to apps/server/dist).
RUN npm run build --workspace @repo-risk-radar/server


FROM node:20-bookworm-slim AS runtime

WORKDIR /app

# Python runtime for the agent.
RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*

ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Install production Node deps (server only).
COPY package.json package-lock.json turbo.json ./
COPY apps/server/package.json apps/server/package.json
COPY apps/client/package.json apps/client/package.json

RUN npm ci --omit=dev --workspace @repo-risk-radar/server

# Copy server build artifacts from builder.
COPY --from=builder /app/apps/server/dist apps/server/dist

# Copy Python agent and install it into the container environment.
COPY apps/agent apps/agent
RUN python3 -m pip install --no-cache-dir --upgrade pip \
  && python3 -m pip install --no-cache-dir ./apps/agent

# Render sets PORT automatically.
ENV PORT=4000

EXPOSE 4000

CMD ["node", "apps/server/dist/main.js"]

