# Frontend Dockerfile - Multi-stage build
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY --chown=node:node . .

# Install all dependencies (including dev for building)
RUN npm ci

# Build the application
RUN npm run build


# Production stage
FROM node:20-alpine as runner

# Set working directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy package files and install production dependencies only
COPY --from=builder --chown=nextjs:nodejs /app/package*.json ./
RUN npm ci --only=production

# Copy built application from builder
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Run the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]
