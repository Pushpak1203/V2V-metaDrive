# metadrive_env/env_manager.py

import os
import yaml
from metadrive import MetaDriveEnv
from .vehicle_manager import VehicleManager


class EnvManager:
    def __init__(self, config_path="config/sim_params.yaml"):
        self.config = self._load_config(config_path)
        self.env = None
        self.vehicles = {}
        self.vehicle_manager = VehicleManager()  # 🔑 Attach VehicleManager here

    def _load_config(self, path):
        """Load sim_params.yaml"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def start_env(self):
        """Initialize MetaDrive environment with config."""
        env_config = {
            "use_render": True,
            "manual_control": False,
            "map": self.config.get("default_map", "CloverLeaf"),
            "traffic_density": 0.1,
            "start_seed": 0,
            "horizon": int(self.config.get("simulation_time", 60) / self.config.get("tick_rate", 0.05)),
            "vehicle_config": {
                "lidar": self.config.get("lidar", {}),
                "camera": self.config.get("camera", {})
            }
        }
        print(f"[ENV] Starting MetaDrive with map={env_config['map']} and horizon={env_config['horizon']}")
        self.env = MetaDriveEnv(env_config)
        self.env.reset()

        # Spawn vehicles from config
        self._spawn_vehicles()

    def _spawn_vehicles(self):
        """Spawn ego and other vehicles from config file."""
        vehicle_ids = self.config.get("vehicle_ids", ["ego_vehicle"])
        count = self.config.get("vehicle_count", len(vehicle_ids))

        for i, vid in enumerate(vehicle_ids[:count]):
            if i == 0:
                # Ego vehicle is managed by env automatically
                self.vehicles[vid] = self.env.vehicle
                print(f"[ENV] Spawned ego vehicle: {vid}")
            else:
                # Add traffic vehicles
                v = self.env.engine.spawn_object(self.env.vehicle_class, vehicle_config={}, random_seed=i)
                self.env.engine.add_policy(v.id, None)  # autopilot-like
                self.vehicles[vid] = v
                print(f"[ENV] Spawned traffic vehicle: {vid} -> {v.id}")

    def get_vehicle(self, vehicle_id):
        """Retrieve a vehicle by ID."""
        return self.vehicles.get(vehicle_id, None)

    # 🔑 Delegate control methods to VehicleManager
    def apply_brake(self, vehicle_id):
        v = self.get_vehicle(vehicle_id)
        if v:
            self.vehicle_manager.apply_brake(v)

    def apply_slowdown(self, vehicle_id):
        v = self.get_vehicle(vehicle_id)
        if v:
            self.vehicle_manager.apply_slowdown(v)

    def keep_speed(self, vehicle_id):
        v = self.get_vehicle(vehicle_id)
        if v:
            self.vehicle_manager.keep_speed(v)

    def follow_path(self, vehicle_id, path):
        v = self.get_vehicle(vehicle_id)
        if v:
            self.vehicle_manager.follow_path(v, path)

    def step(self, action=None):
        """Step environment (apply action to ego vehicle)."""
        if action is None:
            action = [0.0, 0.0]  # [steering, throttle]
        obs, reward, done, info = self.env.step(action)
        return obs, reward, done, info

    def close(self):
        """Close environment cleanly."""
        if self.env:
            self.env.close()
            print("[ENV] Closed MetaDrive environment")
