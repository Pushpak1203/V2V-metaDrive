# communication/receiver.py

import argparse
import socket
import json
import yaml
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.encryption import EncryptionManager
from decision_engine.response_planner import ResponsePlanner


def load_config(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARNING] Failed to load config {path}: {e}")
    return {}


class Receiver:
    def __init__(self, vehicle_id, sim_type, listen_port, v2v_config_path, thresholds_path="config/thresholds.yaml"):
        self.vehicle_id = vehicle_id
        self.sim_type = sim_type
        self.listen_port = listen_port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind(("0.0.0.0", self.listen_port))

        self.v2v_config = load_config(v2v_config_path)
        self.encryption = EncryptionManager(self.v2v_config)

        self.response_planner = ResponsePlanner(vehicle_id, thresholds_path)

        print(f"[RECEIVER] {self.vehicle_id} listening on port {self.listen_port}")

    def receive_loop(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                raw = self.encryption.decrypt(data)
                msg = json.loads(raw.decode("utf-8"))

                print(f"[RECEIVER] {self.vehicle_id} got from {addr}: {msg}")

                # Example: call decision engine
                vehicle_pos = (0, 0)  # Replace with actual
                obstacles = [msg["state"]]
                decision = self.response_planner.decide_action(vehicle_pos, obstacles)

                print(f"[RECEIVER] {self.vehicle_id} decision -> {decision}")

            except Exception as e:
                print(f"[RECEIVER] Error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle_id", required=True)
    parser.add_argument("--sim_type", choices=["metadrive"], default="metadrive")
    parser.add_argument("--listen_port", type=int, default=5001)
    parser.add_argument("--v2v_config", default="config/v2v_settings.yaml")
    parser.add_argument("--thresholds", default="config/thresholds.yaml")
    args = parser.parse_args()

    rc = Receiver(args.vehicle_id, args.sim_type, args.listen_port, args.v2v_config, args.thresholds)
    rc.receive_loop()


if __name__ == "__main__":
    main()
