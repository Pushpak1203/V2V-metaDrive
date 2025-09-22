# communication/broadcaster.py

<<<<<<< HEAD
import json
import socket
import argparse
import time
import yaml
from encryption.encryption_utils import encrypt_message


class Broadcaster:
    def __init__(self, vehicle_id, sim_type, broadcast_port, v2v_config):
        self.vehicle_id = str(vehicle_id)
        self.sim_type = sim_type.lower()
        self.broadcast_port = broadcast_port
        self.v2v_config = v2v_config or {}

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast_ip = self.v2v_config.get("broadcast_ip", "<broadcast>")

        print(f"[INFO] Broadcaster ready for {self.vehicle_id} ({self.sim_type.upper()})")

    def _get_position_and_obstacles(self):
        """
        Placeholder: Replace with actual MetaDrive integration
        """
        vehicle_pos = {"x": 0.0, "y": 0.0}
        obstacles = [
            {"x": 10.0, "y": 5.0},
            {"x": -3.0, "y": 7.0}
        ]
        return vehicle_pos, obstacles

    def _get_current_speed(self):
        return 10.0  # Placeholder

    def broadcast(self, interval=1.0):
        latency = self.v2v_config.get("latency_ms", 0) / 1000.0
        encryption_enabled = self.v2v_config.get("encryption", False)

        print(f"[INFO] Broadcasting for {self.vehicle_id} every {interval}s "
              f"(encryption={'ON' if encryption_enabled else 'OFF'})")

        while True:
            try:
                vehicle_pos, obstacles = self._get_position_and_obstacles()
                message = {
                    "vehicle_id": self.vehicle_id,
                    "vehicle_pos": vehicle_pos,
                    "current_speed": self._get_current_speed(),
                    "obstacles": obstacles
                }

                raw = json.dumps(message).encode()
                if encryption_enabled:
                    raw = encrypt_message(raw)

                time.sleep(latency)  # simulate network latency
                self.sock.sendto(raw, (self.broadcast_ip, self.broadcast_port))
                print(f"[BROADCAST] Sent {len(obstacles)} obstacles from {self.vehicle_id}")

            except Exception as e:
                print(f"[ERROR] Broadcasting failed: {e}")

            time.sleep(interval)


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="V2V Broadcaster")
    parser.add_argument("--vehicle_id", required=True)
    parser.add_argument("--sim_type", choices=["metadrive"], required=True)
    parser.add_argument("--broadcast_port", type=int, default=5000)
    parser.add_argument("--v2v_config", required=True, help="Path to v2v_settings.yaml")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    v2v_config = load_config(args.v2v_config)

    b = Broadcaster(
        vehicle_id=args.vehicle_id,
        sim_type=args.sim_type,
        broadcast_port=args.broadcast_port,
        v2v_config=v2v_config
    )
    b.broadcast(interval=args.interval)
=======
import argparse
import socket
import time
import json
import yaml
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.encryption import EncryptionManager


def load_config(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    return {}


class Broadcaster:
    def __init__(self, vehicle_id, sim_type, broadcast_port, v2v_config_path, interval=1.0):
        self.vehicle_id = vehicle_id
        self.sim_type = sim_type
        self.broadcast_port = broadcast_port
        self.interval = interval

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Load encryption
        self.v2v_config = load_config(v2v_config_path)
        self.encryption = EncryptionManager(self.v2v_config)

        print(f"[BROADCASTER] Vehicle {self.vehicle_id} broadcasting on port {self.broadcast_port}")

    def broadcast_loop(self):
        while True:
            # Example message
            msg = {
                "vehicle_id": self.vehicle_id,
                "timestamp": time.time(),
                "state": {
                    "x": 10.0,
                    "y": 5.0,
                    "speed": 12.3
                }
            }

            raw = json.dumps(msg).encode("utf-8")
            payload = self.encryption.encrypt(raw)

            self.sock.sendto(payload, ("255.255.255.255", self.broadcast_port))
            print(f"[BROADCASTER] {self.vehicle_id} sent -> {msg}")

            time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_id", required=True)
    parser.add_argument("--sim_type", choices=["metadrive"], default="metadrive")
    parser.add_argument("--broadcast_port", type=int, default=5000)
    parser.add_argument("--v2v_config", default="config/v2v_settings.yaml")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    bc = Broadcaster(args.vehicle_id, args.sim_type, args.broadcast_port, args.v2v_config, args.interval)
    bc.broadcast_loop()
>>>>>>> a9f887ea93ec4d42118abb2e421d0eee9896e8c2


if __name__ == "__main__":
    main()
