from flask import Flask, render_template, request, jsonify
import socket
import struct
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration file for storing devices
DEVICES_FILE = '/app/data/devices.json'

def load_devices():
    """Load devices from JSON file"""
    if os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_devices(devices):
    """Save devices to JSON file"""
    with open(DEVICES_FILE, 'w') as f:
        json.dump(devices, f, indent=2)

def create_magic_packet(mac_address):
    """Create a magic packet for Wake-on-LAN"""
    # Remove any separators from MAC address
    mac_address = mac_address.replace(':', '').replace('-', '').replace('.', '')
    
    # Convert MAC address to bytes
    mac_bytes = bytes.fromhex(mac_address)
    
    # Create magic packet: 6 bytes of 0xFF followed by 16 repetitions of MAC address
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    
    return magic_packet

def send_wol_packet(mac_address, broadcast_ip='255.255.255.255', port=9):
    """Send Wake-on-LAN packet"""
    try:
        magic_packet = create_magic_packet(mac_address)
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Send the magic packet
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()
        
        return True, "Wake-on-LAN packet sent successfully"
    except Exception as e:
        return False, f"Error sending packet: {str(e)}"

@app.route('/')
def index():
    """Main dashboard page"""
    devices = load_devices()
    return render_template('index.html', devices=devices)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    devices = load_devices()
    return jsonify(devices)

@app.route('/api/devices', methods=['POST'])
def add_device():
    """Add a new device"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'mac' not in data:
        return jsonify({'success': False, 'message': 'Name and MAC address are required'}), 400
    
    devices = load_devices()
    
    # Check if device already exists
    for device in devices:
        if device['mac'].lower() == data['mac'].lower():
            return jsonify({'success': False, 'message': 'Device with this MAC address already exists'}), 400
    
    new_device = {
        'id': len(devices) + 1,
        'name': data['name'],
        'mac': data['mac'].upper(),
        'ip': data.get('ip', ''),
        'description': data.get('description', ''),
        'last_woken': None,
        'wake_count': 0
    }
    
    devices.append(new_device)
    save_devices(devices)
    
    return jsonify({'success': True, 'device': new_device})

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device"""
    devices = load_devices()
    devices = [d for d in devices if d['id'] != device_id]
    save_devices(devices)
    
    return jsonify({'success': True})

@app.route('/api/wake/<int:device_id>', methods=['POST'])
def wake_device(device_id):
    """Wake a specific device"""
    devices = load_devices()
    device = next((d for d in devices if d['id'] == device_id), None)
    
    if not device:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    
    success, message = send_wol_packet(device['mac'])
    
    if success:
        # Update device statistics
        device['last_woken'] = datetime.now().isoformat()
        device['wake_count'] = device.get('wake_count', 0) + 1
        save_devices(devices)
        
        app.logger.info(f"Wake-on-LAN sent to {device['name']} ({device['mac']})")
    
    return jsonify({
        'success': success,
        'message': message,
        'device': device
    })

@app.route('/api/wake-all', methods=['POST'])
def wake_all_devices():
    """Wake all devices"""
    devices = load_devices()
    results = []
    
    for device in devices:
        success, message = send_wol_packet(device['mac'])
        if success:
            device['last_woken'] = datetime.now().isoformat()
            device['wake_count'] = device.get('wake_count', 0) + 1
        
        results.append({
            'device': device['name'],
            'success': success,
            'message': message
        })
    
    save_devices(devices)
    
    return jsonify({
        'success': True,
        'results': results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
