# Wake-on-LAN Dashboard

A beautiful and modern Docker-based Wake-on-LAN dashboard that allows you to remotely wake up devices on your network through an intuitive web interface.

## Features

- 🎨 **Beautiful Modern UI** - Clean, responsive design with gradient backgrounds and smooth animations
- 🖥️ **Device Management** - Add, edit, and delete network devices with MAC addresses
- ⚡ **One-Click Wake** - Wake individual devices or all devices at once
- 📊 **Statistics Dashboard** - Track wake counts and last wake times
- 🐳 **Docker Ready** - Fully containerized for easy deployment
- 📱 **Mobile Responsive** - Works perfectly on all device sizes
- 💾 **Persistent Storage** - Device configurations are saved between restarts

## Quick Start

### Using Docker Compose (Recommended)

1. Clone or download this repository
2. Navigate to the project directory
3. Run the application:

```bash
docker-compose up -d
```

4. Open your browser and go to `http://localhost:5000`

### Using Docker

```bash
# Build the image
docker build -t wakeonlan-dashboard .

# Run the container
docker run -d \
  --name wakeonlan-dashboard \
  --network host \
  -p 5000:5000 \
  -v $(pwd)/devices.json:/app/devices.json \
  wakeonlan-dashboard
```

### Manual Installation

1. Install Python 3.11+
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python app.py
```

## Configuration

### Network Requirements

- The container needs to run with `--network host` to send Wake-on-LAN packets
- Ensure your target devices have Wake-on-LAN enabled in BIOS/UEFI
- Target devices should be on the same network segment

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Application entry point (default: `app.py`)

## Usage

### Adding Devices

1. Fill in the device form with:
   - **Device Name**: A friendly name for your device
   - **MAC Address**: The network adapter's MAC address (format: XX:XX:XX:XX:XX:XX)
   - **IP Address**: (Optional) The device's IP address
   - **Description**: (Optional) Additional notes about the device

2. Click "Add Device" to save

### Waking Devices

- **Individual Wake**: Click the "Wake Up" button on any device card
- **Wake All**: Use the "Wake All Devices" button to wake all configured devices

### Device Statistics

The dashboard tracks:
- Total number of devices
- Total wake attempts
- Last wake time
- Per-device wake counts and timestamps

## API Endpoints

The application provides a REST API:

- `GET /api/devices` - List all devices
- `POST /api/devices` - Add a new device
- `DELETE /api/devices/{id}` - Delete a device
- `POST /api/wake/{id}` - Wake a specific device
- `POST /api/wake-all` - Wake all devices

## Troubleshooting

### Wake-on-LAN Not Working

1. **Check BIOS/UEFI Settings**: Ensure Wake-on-LAN is enabled
2. **Network Configuration**: Verify the device is on the same network
3. **MAC Address**: Double-check the MAC address format and accuracy
4. **Power Settings**: On Windows, check network adapter power management settings
5. **Firewall**: Ensure UDP port 9 is not blocked

### Container Issues

1. **Network Mode**: Ensure the container runs with `--network host`
2. **Permissions**: The container may need `NET_ADMIN` capability
3. **Port Conflicts**: Check if port 5000 is available

## Security Considerations

- This application is designed for internal network use
- Consider using a reverse proxy with authentication for external access
- The application stores device information in plain text
- No built-in authentication - add your own if needed

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python app.py
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t my-wakeonlan:latest .

# Multi-architecture build
docker buildx build --platform linux/amd64,linux/arm64 -t my-wakeonlan:latest .
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
