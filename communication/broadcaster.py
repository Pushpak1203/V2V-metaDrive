# communication/broadcaster.py
import socket
import argparse
import time
import yaml
import json
from communication.encryption import EncryptionManager
from communication.message_format import encode_message

import metadrive  # Placeholder (replace with your MetaDrive vehicle access)


class Broadcaster:
    def __init__(self, vehicle_id, v2v_config_path="config/v2v_settings.yaml"):
        self.vehicle_id = str(vehicle_id)

        # Load config
        with open(v2v_config_path, "r") as f:
            self.v2v_config = yaml.safe_load(f)

        self.port = self.v2v_config.get("broadcast_port", 5000)
        self.ip = self.v2v_config.get("broadcast_ip", "<broadcast>")
        self.latency = self.v2v_config.get("latency_ms", 0) / 1000.0
        self.encryption_enabled = self.v2v_config.get("encryption_enabled", False)

        # UDP socket for broadcasting
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Encryption setup
        self.encryption = None
        if self.encryption_enabled:
            key_b64 = self.v2v_config.get("encryption_key_b64")
            self.encryption = EncryptionManager(key_b64)

        print(f"[BROADCASTER] Vehicle {self.vehicle_id} ready (port {self.port}, encryption={self.encryption_enabled})")

    def _get_position_and_obstacles(self):
        """
        Placeholder: Replace with actual MetaDrive environment hooks.
        For now, returns dummy values.
        """
        vehicle_pos = {"x": 10.0, "y": 20.0}
        obstacles = [{"x": 12.0, "y": 22.0}, {"x": 15.0, "y": 25.0}]
        return vehicle_pos, obstacles

    def _get_current_speed(self):
        """
        Placeholder for MetaDrive vehicle speed.
        """
        return 12.5

    def broadcast(self, interval=1.0):
        """
        Broadcasts encrypted position + obstacle data periodically.
        """
        while True:
            vehicle_pos, obstacles = self._get_position_and_obstacles()
            message = encode_message(
                self.vehicle_id,
                vehicle_pos,
                self._get_current_speed(),
                obstacles
            )

            if self.encryption:
                message = self.encryption.encrypt(message)

            self.sock.sendto(message, (self.ip, self.port))
            print(f"[BROADCAST] Sent {len(obstacles)} obstacles for vehicle {self.vehicle_id}")
            time.sleep(interval + self.latency)


def main():
    parser = argparse.ArgumentParser(description="V2V Broadcaster for MetaDrive Vehicles")
    parser.add_argument("--vehicle_id", required=True, help="Vehicle ID")
    parser.add_argument("--v2v_config", default="config/v2v_settings.yaml", help="Path to V2V config file")
    args = parser.parse_args()

    broadcaster = Broadcaster(args.vehicle_id, v2v_config_path=args.v2v_config)
    broadcaster.broadcast()


if __name__ == "__main__":
    main()
