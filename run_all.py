# run_all.py
import argparse
import subprocess
import time
import os
import yaml
from multiprocessing import Process

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
SIM_PARAMS_FILE = os.path.join(CONFIG_DIR, "sim_params.yaml")
V2V_CONFIG_FILE = os.path.join(CONFIG_DIR, "v2v_settings.yaml")
THRESHOLDS_FILE = os.path.join(CONFIG_DIR, "thresholds.yaml")


def load_config(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def start_metadrive():
    # MetaDrive is imported inside the broadcaster/receiver scripts
    print("[MASTER] MetaDrive environment will be started by env_manager.")
    return None  # Nothing to launch externally like CARLA


def run_broadcaster(sim_type, broadcast_port, sim_params_path, v2v_config_path, thresholds_path, vehicle_id):
    print("[MASTER] Starting broadcaster...")
    subprocess.run([
        "python", "communication/broadcaster.py",
        "--sim_type", sim_type,
        "--broadcast_port", str(broadcast_port),
        "--sim_params", sim_params_path,
        "--v2v_config", v2v_config_path,
        "--thresholds", thresholds_path,
        "--vehicle_id", str(vehicle_id)
    ])


def run_receiver(vehicle_id, sim_type, listen_port, sim_params_path, v2v_config_path, thresholds_path):
    print(f"[MASTER] Starting receiver for vehicle {vehicle_id}...")
    subprocess.run([
        "python", "communication/receiver.py",
        "--vehicle_id", str(vehicle_id),
        "--sim_type", sim_type,
        "--listen_port", str(listen_port),
        "--sim_params", sim_params_path,
        "--v2v_config", v2v_config_path,
        "--thresholds", thresholds_path
    ])


def main():
    parser = argparse.ArgumentParser(description="Master script to run MetaDrive + Broadcaster + Receivers")
    parser.add_argument("--sim_type", choices=["metadrive"], default="metadrive",
                        help="Simulation backend (default: metadrive)")
    parser.add_argument("--vehicle_ids", nargs="+", help="Vehicle IDs to simulate")
    parser.add_argument("--broadcast_port", type=int, help="UDP port for broadcaster")
    parser.add_argument("--receiver_base_port", type=int, help="Base UDP port for receivers")
    args = parser.parse_args()

    # Load configs
    sim_params = load_config(SIM_PARAMS_FILE)
    v2v_config = load_config(V2V_CONFIG_FILE)
    thresholds = load_config(THRESHOLDS_FILE)

    # Defaults from configs if not provided via CLI
    vehicle_ids = args.vehicle_ids or sim_params.get("vehicle_ids", ["ego_vehicle"])
    broadcast_port = args.broadcast_port or sim_params.get("broadcast_port", 5000)
    receiver_base_port = args.receiver_base_port or sim_params.get("receiver_base_port", 5001)

    processes = []

    # MetaDrive start (lazy init inside env_manager)
    start_metadrive()
    time.sleep(2)

    # Start Broadcaster for ego vehicle
    p_broadcaster = Process(
        target=run_broadcaster,
        args=(args.sim_type, broadcast_port, SIM_PARAMS_FILE, V2V_CONFIG_FILE, THRESHOLDS_FILE, vehicle_ids[0])
    )
    p_broadcaster.start()
    processes.append(p_broadcaster)
    time.sleep(2)

    # Start Receivers for all vehicles
    for i, vid in enumerate(vehicle_ids):
        listen_port = receiver_base_port + i
        p_recv = Process(
            target=run_receiver,
            args=(vid, args.sim_type, listen_port, SIM_PARAMS_FILE, V2V_CONFIG_FILE, THRESHOLDS_FILE)
        )
        p_recv.start()
        processes.append(p_recv)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("[MASTER] Shutting down all processes...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()
