# ============================================================
#  Stage 1: BUILD — install deps + produce Vite production bundle
# ============================================================
FROM node:22-alpine AS builder

WORKDIR /app

# 1) Copy lockfile + package.json first (Docker layer cache)
COPY package.json package-lock.json ./

# 2) Install dependencies
#    Using npm install (not npm ci) for cross-npm-version lockfile compat
RUN npm install --ignore-scripts

# 3) Copy source files
COPY index.html       ./
COPY vite.config.ts   ./
COPY tsconfig.json    ./
COPY tsconfig.app.json ./
COPY vite-env.d.ts    ./
COPY public/          ./public/
COPY src/             ./src/

# 4) Build production bundle
#    VITE_API_URL is baked in at build-time; override via --build-arg
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# ============================================================
#  Stage 2: SERVE — lightweight nginx image for static serving
# ============================================================
FROM nginx:1.27-alpine AS production

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy custom nginx config
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Non-root user (best practice 2026)
RUN chown -R nginx:nginx /usr/share/nginx/html \
 && chmod -R 755 /usr/share/nginx/html \
 && chown -R nginx:nginx /var/cache/nginx \
 && chown -R nginx:nginx /var/log/nginx \
 && chown -R nginx:nginx /etc/nginx/conf.d \
 && touch /var/run/nginx.pid \
 && chown -R nginx:nginx /var/run/nginx.pid

USER nginx

EXPOSE 80

# Health-check for Docker / orchestrators
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
