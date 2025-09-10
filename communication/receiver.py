# communication/receiver.py

import socket
import argparse
import yaml
import os
import sys
import time

# Add the parent directory to sys.path to resolve package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from communication.encryption import EncryptionManager
from communication.message_format import decode_message
from decision_engine.response_planner import ResponsePlanner


def main():
    parser = argparse.ArgumentParser(description="V2V Receiver")
    parser.add_argument("--vehicle_id", required=True, help="ID of this vehicle")
    parser.add_argument("--sim_type", required=True, help="Simulation backend type")
    parser.add_argument("--listen_port", type=int, required=True, help="UDP port to listen on")
    parser.add_argument("--v2v_config", required=True, help="Path to v2v_settings.yaml")
    parser.add_argument("--thresholds", required=True, help="Path to thresholds.yaml")  # ✅ absolute path
    args = parser.parse_args()

    print(f"[RECEIVER] Vehicle {args.vehicle_id} listening on port {args.listen_port}")

    # Load V2V configuration
    with open(args.v2v_config, "r") as f:
        v2v_config = yaml.safe_load(f)

    # Load thresholds configuration ✅ using absolute path
    with open(args.thresholds, "r") as f:
        thresholds = yaml.safe_load(f)

    # Initialize encryption and planner
    encryption = EncryptionManager(v2v_config)
    planner = ResponsePlanner(args.vehicle_id, config_path=args.thresholds)

    # Setup UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", args.listen_port))
    sock.settimeout(1.0)

    print(f"[RECEIVER] Started for {args.vehicle_id}")

    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                if encryption.enabled:
                    data = encryption.decrypt(data)

                message = decode_message(data)
                vehicle_pos = message.get("vehicle_pos", [0, 0])
                current_speed = message.get("current_speed", 0)
                obstacles = message.get("obstacles", [])

                action = planner.decide_action(vehicle_pos, obstacles, current_speed)

                print(f"[RECEIVER] Action for {args.vehicle_id}: {action}")

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[RECEIVER] Error: {e}")
    except KeyboardInterrupt:
        print(f"[RECEIVER] Vehicle {args.vehicle_id} shutting down.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
