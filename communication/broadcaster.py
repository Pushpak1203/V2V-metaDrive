# communication/broadcaster.py

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


if __name__ == "__main__":
    main()
