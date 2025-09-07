# run_all.py
import argparse
import subprocess
import time
import os
import sys
import yaml
from multiprocessing import Process

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
COMM_DIR = os.path.join(BASE_DIR, "communication")

SIM_PARAMS_FILE = os.path.join(CONFIG_DIR, "sim_params.yaml")
V2V_CONFIG_FILE = os.path.join(CONFIG_DIR, "v2v_settings.yaml")

def load_config(file_path, key=None):
    """Load a YAML config file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
            if key:
                return data.get(key)
            return data
    return None

def run_broadcaster(vehicle_id, sim_type, broadcast_port, v2v_config_path):
    """Start broadcaster process with absolute path."""
    print(f"[MASTER] Starting broadcaster for {vehicle_id}...")
    subprocess.run([
        sys.executable, os.path.join(COMM_DIR, "broadcaster.py"),
        "--vehicle_id", str(vehicle_id),
        "--sim_type", sim_type,
        "--broadcast_port", str(broadcast_port),
        "--v2v_config", v2v_config_path
    ])

def run_receiver(vehicle_id, sim_type, listen_port, v2v_config_path):
    """Start receiver process with absolute path."""
    print(f"[MASTER] Starting receiver for vehicle {vehicle_id}...")
    subprocess.run([
        sys.executable, os.path.join(COMM_DIR, "receiver.py"),
        "--vehicle_id", str(vehicle_id),
        "--sim_type", sim_type,
        "--listen_port", str(listen_port),
        "--v2v_config", v2v_config_path
    ])

def main():
    parser = argparse.ArgumentParser(description="Master script to run MetaDrive + Broadcaster + Receivers")
    parser.add_argument("--sim_type", choices=["metadrive"], default="metadrive", help="Simulation backend to use")
    parser.add_argument("--vehicle_ids", nargs="+", help="Vehicle IDs (overrides sim_params.yaml)")
    parser.add_argument("--broadcast_port", type=int, help="UDP port for broadcaster")
    parser.add_argument("--receiver_base_port", type=int, help="Base UDP port for receivers")
    args = parser.parse_args()

    # Load configs
    sim_params = load_config(SIM_PARAMS_FILE) or {}
    v2v_config = load_config(V2V_CONFIG_FILE) or {}

    # Apply defaults from sim_params.yaml if not provided
    vehicle_ids = args.vehicle_ids or sim_params.get("vehicle_ids", ["ego_vehicle"])
    broadcast_port = args.broadcast_port or sim_params.get("broadcast_port", 5000)
    receiver_base_port = args.receiver_base_port or sim_params.get("receiver_base_port", 5001)

    print("[MASTER] MetaDrive environment will be started by env_manager.")

    processes = []

    # Start one Broadcaster per vehicle
    for vid in vehicle_ids:
        p_broadcaster = Process(target=run_broadcaster, args=(vid, args.sim_type, broadcast_port, V2V_CONFIG_FILE))
        p_broadcaster.start()
        processes.append(p_broadcaster)
        time.sleep(1)  # stagger start

    # Start Receivers for all vehicles
    for i, vid in enumerate(vehicle_ids):
        listen_port = receiver_base_port + i
        p_recv = Process(target=run_receiver, args=(vid, args.sim_type, listen_port, V2V_CONFIG_FILE))
        p_recv.start()
        processes.append(p_recv)

    # Wait for all processes
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("[MASTER] Shutting down all processes...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
