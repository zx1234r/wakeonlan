# Portainer Stack Deployment Guide

This guide will help you deploy the Wake-on-LAN Dashboard using Portainer Stacks.

## Method 1: Build and Push to Registry (Recommended)

### Step 1: Build and Tag the Image
```bash
# Build the image locally
docker build -t wakeonlan-dashboard:latest .

# Tag for your registry (replace with your registry URL)
docker tag wakeonlan-dashboard:latest your-registry.com/wakeonlan-dashboard:latest

# Push to registry
docker push your-registry.com/wakeonlan-dashboard:latest
```

### Step 2: Update Stack Configuration
Update the `image` line in `portainer-stack.yml`:
```yaml
image: your-registry.com/wakeonlan-dashboard:latest
```

### Step 3: Deploy in Portainer
1. Open Portainer web interface
2. Go to **Stacks** → **Add stack**
3. Choose **Web editor**
4. Copy the contents of `portainer-stack.yml`
5. Name your stack (e.g., "wakeonlan-dashboard")
6. Click **Deploy the stack**

## Method 2: Git Repository Deployment

### Step 1: Push Code to Git Repository
```bash
git init
git add .
git commit -m "Initial Wake-on-LAN dashboard"
git remote add origin https://github.com/yourusername/wakeonlan-dashboard.git
git push -u origin main
```

### Step 2: Deploy from Repository
1. In Portainer, go to **Stacks** → **Add stack**
2. Choose **Repository**
3. Enter your Git repository URL
4. Set compose file path: `docker-compose.yml`
5. Click **Deploy the stack**

## Method 3: Local Build (If Portainer has access to build context)

If your Portainer instance can access the build context, use this stack configuration:

```yaml
version: '3.8'

services:
  wakeonlan:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: wakeonlan-dashboard
    ports:
      - "5000:5000"
    volumes:
      - wakeonlan_data:/app/data
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - wakeonlan_network

volumes:
  wakeonlan_data:
    driver: local

networks:
  wakeonlan_network:
    driver: bridge
```

## Configuration Options

### Environment Variables
You can customize the deployment by adding these environment variables:

```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
  - FLASK_HOST=0.0.0.0
  - FLASK_PORT=5000
```

### Port Configuration
Change the external port by modifying the ports section:
```yaml
ports:
  - "8080:5000"  # Access via port 8080
```

### Traefik Integration
If you're using Traefik, update the labels:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.wakeonlan.rule=Host(`wol.yourdomain.com`)"
  - "traefik.http.services.wakeonlan.loadbalancer.server.port=5000"
  - "traefik.docker.network=traefik_default"
```

### Volume Persistence
The stack uses a named volume for data persistence:
```yaml
volumes:
  wakeonlan_data:
    driver: local
```

This ensures your device configurations persist across container restarts.

## Network Considerations for Wake-on-LAN

### Host Network Mode (Linux only)
If you're running on a Linux Docker host and need direct network access:

```yaml
services:
  wakeonlan:
    # ... other config
    network_mode: host
    # Remove the ports section when using host mode
```

### Bridge Network with Broadcast
For most setups, the default bridge network works fine. The container will send WoL packets from its network namespace.

## Accessing the Dashboard

After deployment, access the dashboard at:
- `http://your-server-ip:5000`
- Or via your configured domain if using Traefik

## Troubleshooting

### Container Won't Start
Check Portainer logs:
1. Go to **Stacks** → Your stack → **Containers**
2. Click on the container name
3. View **Logs** tab

### Wake-on-LAN Not Working
1. Ensure target devices have WoL enabled in BIOS
2. Check network connectivity between container and target devices
3. Verify MAC addresses are correct
4. Consider using host networking if on Linux

### Port Already in Use
If port 5000 is busy, change the external port:
```yaml
ports:
  - "5001:5000"  # Use port 5001 instead
```

## Security Recommendations

1. **Reverse Proxy**: Use Traefik or Nginx for HTTPS
2. **Authentication**: Add auth middleware if exposing externally
3. **Network Isolation**: Use Docker networks to isolate the container
4. **Firewall**: Restrict access to necessary ports only

## Updating the Application

To update the deployed stack:
1. Build and push new image version
2. Update stack configuration in Portainer
3. Click **Update the stack**
4. Portainer will pull new image and recreate containers
