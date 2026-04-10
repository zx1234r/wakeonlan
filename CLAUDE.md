# Wake-on-LAN Dashboard — CLAUDE.md

## Project Overview
Flask-based web dashboard for sending Wake-on-LAN (WoL) magic packets to network devices.
Single-page app with device CRUD and one-click wake. No auth — internal network use only.

## Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask 2.3.3 |
| Frontend | Vanilla JS + Jinja2 templates (index.html) |
| Storage | JSON file at `/app/data/devices.json` |
| Container | Docker (GHCR image: `ghcr.io/zx1234r/wakeonlan:latest`) |
| CI/CD | GitHub Actions → GHCR |
| Reverse proxy | Traefik (optional) |

## File Map
```
app.py                    # All backend logic (routes + WoL socket code)
templates/index.html      # Single frontend template
data/devices.json         # Persistent device store (volume-mounted)
docker-compose.yml        # Local dev / bridge-network deployment
portainer-stack.yml       # Portainer deployment (bridge network)
Dockerfile                # python:3.11-slim, port 5000, /app/data volume
requirements.txt          # flask, werkzeug only
```

## API Routes
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Dashboard HTML |
| GET | `/api/devices` | List all devices |
| POST | `/api/devices` | Add device `{name, mac, ip?, description?}` |
| DELETE | `/api/devices/<id>` | Remove device |
| POST | `/api/wake/<id>` | Send WoL to one device |
| POST | `/api/wake-all` | Send WoL to all devices |

## WoL Packet Implementation (`app.py:27-55`)
- **Protocol**: UDP, pure Python `socket` module (no external WoL library)
- **Magic packet**: `\xFF * 6` + `MAC_bytes * 16` = 102 bytes
- **Default target**: `255.255.255.255` (global broadcast), **port 9**
- `SO_BROADCAST` socket option enabled

## Critical Known Issue: Docker Bridge Networking
**WoL packets sent from inside a Docker bridge-network container do NOT reach the physical LAN.**
The `255.255.255.255` broadcast is confined to the container's virtual network.

### Fix (Linux Docker host)
Add `network_mode: host` to the stack and remove port/network definitions:
```yaml
services:
  wakeonlan:
    image: ...
    network_mode: host   # container uses host's physical NIC directly
    # remove: ports, networks blocks
```

### Fix (alternative — subnet-directed broadcast)
Set `BROADCAST_IP` env var to subnet broadcast (e.g., `192.168.1.255`) AND use host networking.
Modify `app.py:117` to read from env:
```python
broadcast_ip = os.environ.get('BROADCAST_IP', '255.255.255.255')
success, message = send_wol_packet(device['mac'], broadcast_ip=broadcast_ip)
```

### Windows Docker Desktop
`network_mode: host` is NOT supported. Run the container on a Linux host instead,
or use an alternative tool on the Windows host directly.

## Device Data Schema
```json
{
  "id": 1,
  "name": "string",
  "mac": "XX:XX:XX:XX:XX:XX",
  "ip": "192.168.1.x",
  "description": "string",
  "last_woken": "ISO8601 | null",
  "wake_count": 0
}
```

## Deployment
- **Portainer stack**: `portainer-stack.yml` (currently bridge network — see issue above)
- **docker-compose**: `docker-compose.yml` (same bridge issue on Windows)
- **Port**: 5000 (web UI)
- **Volume**: `/app/data` must be mounted for persistence

## Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `FLASK_ENV` | `production` | Flask mode |
| `PYTHONUNBUFFERED` | `1` | Real-time logs |
| `BROADCAST_IP` | `255.255.255.255` (not yet impl.) | WoL target |
