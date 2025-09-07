# communication/broadcaster.py

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


if __name__ == "__main__":
    main()
