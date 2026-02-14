# Todo-Chat Helm Chart Deployment Guide

## Overview

The Helm chart in `todo-chat/` has been updated to deploy your full-stack application with:
- **Frontend**: Next.js application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **Database**: External PostgreSQL (Neon)
- **Optional**: OpenAI integration for chat

## Prerequisites

1. **Minikube running**: `minikube start`
2. **Docker images built**:
   - `todo-frontend:latest`
   - `todo-backend:latest`
3. **Helm installed**: `helm version`
4. **Ingress controller** (optional, for local domain routing):
   ```bash
   minikube addons enable ingress
   ```

## Prepare Docker Images for Minikube

Load your locally built images into Minikube's Docker daemon:

```bash
# Point your shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Navigate to project directory
cd /mnt/e/7. Low\ Code\ Agentic\ AI/Hackathon\ II/phase-IV

# Rebuild images (or ensure they exist)
docker build -t todo-frontend:latest frontend/
docker build -t todo-backend:latest backend/

# Reset Docker environment to your host (optional)
eval $(docker-machine env -u)
```

## Configure Deployment

The `todo-chat/values.yaml` is pre-configured with:
- ✅ Neon PostgreSQL URL
- ✅ Frontend and backend image names
- ✅ Port configurations
- ✅ Resource limits

**Optional updates to `values.yaml`**:

```yaml
global:
  openaiApiKey: "your-openai-api-key-here"  # For chat functionality
  secretKey: "change-this-to-a-strong-secret"  # Change for production!
  betterAuthSecret: "change-this-too"  # Change for production!
```

## Deploy with Helm

```bash
cd /mnt/e/7. Low\ Code\ Agentic\ AI/Hackathon\ II/phase-IV

# Install or upgrade the release
helm upgrade --install todo-chat ./todo-chat --namespace default
```

## Access the Application

### Option 1: Port-Forward (Recommended for local testing)

```bash
# Forward frontend
kubectl port-forward service/todo-chat-frontend 3000:3000 &

# Forward backend
kubectl port-forward service/todo-chat-backend 8000:8000 &
```

Now access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Minikube Service URLs

```bash
# Get frontend URL
minikube service todo-chat-frontend --url

# Get backend URL
minikube service todo-chat-backend --url
```

### Option 3: Ingress (if enabled)

```bash
# Update your /etc/hosts file to map the hostname to Minikube IP
echo "$(minikube ip) todo-chat.local" | sudo tee -a /etc/hosts

# Access via ingress
curl http://todo-chat.local  # Frontend
curl http://todo-chat.local/api  # Backend (may need browser)
```

## Verify Deployment

```bash
# Check all resources
kubectl get all -l app.kubernetes.io/instance=todo-chat

# Check pods status
kubectl get pods -l app.kubernetes.io/instance=todo-chat

# Check services
kubectl get svc -l app.kubernetes.io/instance=todo-chat

# Check ingress (if enabled)
kubectl get ingress
```

## View Logs

```bash
# Frontend logs
kubectl logs -f deployment/todo-chat-frontend

# Backend logs
kubectl logs -f deployment/todo-chat-backend

# All pods with label
kubectl logs -f -l app.kubernetes.io/instance=todo-chat -c frontend
kubectl logs -f -l app.kubernetes.io/instance=todo-chat -c backend
```

## Test the Application

1. Open http://localhost:3000 (frontend)
2. Click "Create Account"
3. Register a new user
4. You should be redirected to the dashboard
5. Test sign-out and sign-in again

## Troubleshooting

### Pods not starting
```bash
# Describe pod for errors
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Images not found
```bash
# Check Minikube's Docker environment
eval $(minikube docker-env)
docker images | grep todo

# If images missing, rebuild them
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
```

### Ingress not working
```bash
# Check ingress controller is running
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl describe ingress todo-chat

# Test DNS resolution
nslookup todo-chat.local
```

### Backend can't connect to database
- Verify `DATABASE_URL` in `values.yaml` is correct
- Check Neon dashboard for connection status
- Ensure SSL mode is set correctly

## Cleanup

```bash
# Delete Helm release
helm uninstall todo-chat

# Delete remaining resources
kubectl delete deployment,todo-chat-service -l app.kubernetes.io/instance=todo-chat
```

## Notes

- The frontend runs as a non-root user (nextjs) for security
- The backend runs as a non-root user (app)
- Probes are configured for health checks
- Resources are limited for Minikube compatibility
- Database is external (Neon) - no PVC needed
- Chat functionality requires OpenAI API key to be set

## Next Steps

1. Set up proper container registry (Docker Hub, GitHub Container Registry, etc.)
2. Update `values.yaml` image.repository to use registry URLs
3. Add TLS for production (update ingress.tls)
4. Configure proper secrets management (Kubernetes Secrets)
5. Set up monitoring and logging
