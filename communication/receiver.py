# communication/receiver.py

import json
import socket
import argparse
import yaml
from encryption.encryption_utils import decrypt_message
from decision_engine.response_planner import ResponsePlanner
from metadrive_env.vehicle_manager import (
    apply_brake,
    apply_slowdown,
    keep_speed,
    follow_path
)


class Receiver:
    def __init__(self, vehicle_id, sim_type, listen_port, config_path, v2v_config):
        self.vehicle_id = str(vehicle_id)
        self.sim_type = sim_type.lower()
        self.listen_port = listen_port
        self.response_planner = ResponsePlanner(vehicle_id, config_path)

        self.v2v_config = v2v_config or {}
        self.encryption_enabled = self.v2v_config.get("encryption", False)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.listen_port))
        print(f"[INFO] Receiver {self.vehicle_id} listening on {self.listen_port}")

    def listen(self):
        while True:
            data, addr = self.sock.recvfrom(4096)
            try:
                raw = decrypt_message(data) if self.encryption_enabled else data
                message = json.loads(raw.decode())
                self._process_message(message)
            except Exception as e:
                print(f"[ERROR] Failed to process: {e}")

    def _process_message(self, message):
        obstacles = message.get("obstacles", [])
        vehicle_pos = message.get("vehicle_pos")
        current_speed = message.get("current_speed", 10.0)

        if not vehicle_pos or not isinstance(obstacles, list):
            print("[WARNING] Incomplete message")
            return

        for obs in obstacles:
            action = self.response_planner.decide_action(
                (vehicle_pos["x"], vehicle_pos["y"]),
                (obs["x"], obs["y"]),
                current_speed=current_speed
            )
            print(f"[DECISION] {self.vehicle_id}: {action} for obstacle {obs}")

            self._apply_action(action)

    def _apply_action(self, action):
        if action == "BRAKE":
            apply_brake(self.vehicle_id)
        elif action == "SLOW_DOWN":
            apply_slowdown(self.vehicle_id)
        elif action == "KEEP_SPEED":
            keep_speed(self.vehicle_id)
        elif action == "REROUTE":
            path = self.response_planner.plan_reroute(self.vehicle_id)
            follow_path(self.vehicle_id, path)


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="V2V Receiver")
    parser.add_argument("--vehicle_id", required=True)
    parser.add_argument("--sim_type", choices=["metadrive"], required=True)
    parser.add_argument("--listen_port", type=int, default=5001)
    parser.add_argument("--config_path", default="config/thresholds.yaml")
    parser.add_argument("--v2v_config", required=True, help="Path to v2v_settings.yaml")
    args = parser.parse_args()

    v2v_config = load_config(args.v2v_config)

    r = Receiver(
        vehicle_id=args.vehicle_id,
        sim_type=args.sim_type,
        listen_port=args.listen_port,
        config_path=args.config_path,
        v2v_config=v2v_config
    )
    r.listen()


if __name__ == "__main__":
    main()
