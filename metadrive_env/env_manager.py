import os
import time
from metadrive import MetaDriveEnv


class EnvManager:
    """
    Wrapper around MetaDriveEnv to manage environment setup,
    vehicle registry, and stepping simulation.
    """

    def __init__(self, config_path=None, sim_config=None):
        """
        Args:
            config_path: Path to YAML file with environment parameters
            sim_config: Dict (optional) if configs are passed directly
        """
        self.config = sim_config or {}
        self.env = None
        self.vehicles = {}  # {vehicle_id: vehicle_obj}

    def setup_env(self):
        """Initialize MetaDrive environment with configs."""
        # Default environment settings
        env_config = {
            "environment_num": self.config.get("environment_num", 1),
            "traffic_density": self.config.get("traffic_density", 0.1),
            "use_render": self.config.get("use_render", False),
            "manual_control": self.config.get("manual_control", False),
            "start_seed": self.config.get("start_seed", 0),
            "map": self.config.get("default_map", "C"),
            "vehicle_config": {
                "enable_reverse": True,
                "show_navi_mark": True,
            },
        }

        self.env = MetaDriveEnv(env_config)
        obs, _ = self.env.reset()
        print("[ENV] MetaDrive environment initialized.")
        return obs

    def register_vehicle(self, vehicle_id, vehicle_obj):
        """Register a vehicle for tracking in the env."""
        self.vehicles[vehicle_id] = vehicle_obj
        print(f"[ENV] Vehicle {vehicle_id} registered.")

    def get_vehicle(self, vehicle_id):
        """Get vehicle object by ID."""
        return self.vehicles.get(vehicle_id, None)

    def step(self, actions=None):
        """
        Step simulation forward.
        Args:
            actions: Dict {vehicle_id: action} if multi-agent
        """
        if self.env is None:
            raise RuntimeError("Environment not initialized. Call setup_env() first.")

        if actions:
            obs, reward, terminated, truncated, info = self.env.step(actions)
        else:
            obs, reward, terminated, truncated, info = self.env.step({})

        return obs, reward, terminated, truncated, info

    def run_loop(self, steps=1000, sleep_time=0.05):
        """Simple loop for running the environment."""
        for i in range(steps):
            obs, reward, terminated, truncated, info = self.step()
            time.sleep(sleep_time)
            if terminated or truncated:
                print("[ENV] Episode finished. Resetting...")
                self.env.reset()

    def close(self):
        """Close the environment."""
        if self.env:
            self.env.close()
            print("[ENV] MetaDrive environment closed.")
