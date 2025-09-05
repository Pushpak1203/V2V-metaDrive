import json
import socket
import argparse
import yaml
from decision_engine.response_planner import ResponsePlanner
from decision_engine.hybrid_astar import HybridAStar
from metadrive_env.env_manager import EnvManager
from metadrive_env.vehicle_manager import VehicleManager


class Receiver:
    def __init__(self, vehicle_id, sim_type="metadrive",
                 listen_port=5001,
                 sim_params_path="config/sim_params.yaml",
                 v2v_config_path="config/v2v_settings.yaml",
                 thresholds_path="config/thresholds.yaml"):
        self.vehicle_id = str(vehicle_id)
        self.sim_type = sim_type.lower()
        self.listen_port = listen_port

        # Load configs
        self.sim_params = self._load_config(sim_params_path)
        self.v2v_config = self._load_config(v2v_config_path)
        self.thresholds = self._load_config(thresholds_path)

        # UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.listen_port))
        print(f"[INFO] Receiver listening on port {listen_port} for vehicle {vehicle_id}")

        # Initialize planner + Hybrid A*
        self.response_planner = ResponsePlanner(vehicle_id, self.thresholds)
        self.hybrid_astar = HybridAStar()

        # Initialize MetaDrive environment + vehicle manager
        self.env = EnvManager(self.sim_params)
        self.vehicle_manager = VehicleManager(self.env)
        self.vehicle = self.vehicle_manager.get_vehicle(vehicle_id)

    def _load_config(self, path):
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[WARNING] Could not load config {path}: {e}")
            return {}

    def listen(self):
        print(f"[INFO] Vehicle {self.vehicle_id} waiting for V2V messages...")
        while True:
            data, _ = self.sock.recvfrom(8192)
            try:
                message = json.loads(data.decode())
                self._process_message(message)
            except Exception as e:
                print(f"[ERROR] Failed to process message: {e}")

    def _process_message(self, message):
        obstacles = message.get("obstacles", [])
        vehicle_pos = message.get("vehicle_pos")
        current_speed = message.get("current_speed", 5.0)

        if not vehicle_pos:
            print("[WARNING] No vehicle position found in message.")
            return

        # Choose action based on planner
        action = self.response_planner.decide_action(
            (vehicle_pos["x"], vehicle_pos["y"]),
            [(obs["x"], obs["y"]) for obs in obstacles],
            current_speed=current_speed
        )

        print(f"[DECISION] Vehicle {self.vehicle_id} -> {action}")
        self._apply_action(action, vehicle_pos, obstacles)

    def _apply_action(self, action, vehicle_pos, obstacles):
        if action == "BRAKE":
            self.vehicle_manager.apply_brake(self.vehicle)
        elif action == "SLOW_DOWN":
            self.vehicle_manager.apply_slowdown(self.vehicle)
        elif action == "KEEP_SPEED":
            self.vehicle_manager.keep_speed(self.vehicle)
        elif action == "REROUTE":
            self._apply_reroute(vehicle_pos, obstacles)

    def _apply_reroute(self, vehicle_pos, obstacles):
        """Use Hybrid A* planner to compute a new path and send commands."""
        if not obstacles:
            print("[REROUTE] No obstacles found, skipping.")
            return

        start = (vehicle_pos["x"], vehicle_pos["y"], 0.0)  # heading default 0
        goal = (vehicle_pos["x"] + 30, vehicle_pos["y"] + 5, 0.0)  # arbitrary next target

        # Run Hybrid A*
        path = self.hybrid_astar.plan(
            start=start,
            goal=goal,
            obstacles=[(o["x"], o["y"]) for o in obstacles]
        )

        if path:
            print(f"[REROUTE] New path with {len(path)} waypoints computed using Hybrid A*")
            self.vehicle_manager.follow_path(self.vehicle, path)
        else:
            print("[REROUTE] Hybrid A* failed to compute path.")


def main():
    parser = argparse.ArgumentParser(description="MetaDrive V2V Receiver with Hybrid A* rerouting")
    parser.add_argument("--vehicle_id", required=True, help="Vehicle ID in MetaDrive")
    parser.add_argument("--sim_type", choices=["metadrive"], default="metadrive")
    parser.add_argument("--listen_port", type=int, default=5001)
    parser.add_argument("--sim_params", default="config/sim_params.yaml")
    parser.add_argument("--v2v_config", default="config/v2v_settings.yaml")
    parser.add_argument("--thresholds", default="config/thresholds.yaml")
    args = parser.parse_args()

    receiver = Receiver(
        vehicle_id=args.vehicle_id,
        sim_type=args.sim_type,
        listen_port=args.listen_port,
        sim_params_path=args.sim_params,
        v2v_config_path=args.v2v_config,
        thresholds_path=args.thresholds
    )
    receiver.listen()


if __name__ == "__main__":
    main()
