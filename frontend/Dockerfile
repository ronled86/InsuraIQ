FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies (supports absence of package-lock.json)
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY index.html ./
COPY src ./src

# Build static assets
RUN npm run build

# Runtime stage just to place build artifacts in a volume for Caddy
FROM node:20-alpine AS runtime
WORKDIR /app
COPY --from=build /app/dist /opt/build-dist
VOLUME ["/frontend-out"]
CMD sh -c "cp -r /opt/build-dist/* /frontend-out/ 2>/dev/null || true; sleep infinity"
