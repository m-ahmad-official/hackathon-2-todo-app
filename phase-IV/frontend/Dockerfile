# Frontend Dockerfile - Multi-stage build for Next.js
FROM node:20-alpine AS deps

# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production


# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy all files from deps including node_modules (production deps)
COPY --from=deps /app/ ./

# Copy source code
COPY . .

# Install all dependencies including devDependencies (TypeScript, etc.)
RUN npm ci

# Build the application with API base URL from build arg
ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN npm run build


# Production stage
FROM node:20-alpine AS runner

# Set environment to production
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
COPY --from=builder --chown=nextjs:nodejs /app/package-lock.json ./package-lock.json

# Install only production dependencies
RUN npm ci --omit=dev

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set default port for Next.js
ENV PORT=3000 \
    HOSTNAME="0.0.0.0"

# Start the application
CMD ["npm", "start"]
