# decision_engine/response_planner.py

import yaml
import math
from decision_engine.hybrid_astar import HybridAStar


class ResponsePlanner:
    def __init__(self, vehicle_id, config_path="config/thresholds.yaml"):
        self.vehicle_id = vehicle_id

        # Load thresholds from config
        try:
            with open(config_path, "r") as f:
                self.thresholds = yaml.safe_load(f)
        except Exception as e:
            print(f"[WARNING] Could not load thresholds config: {e}")
            # Default values as fallback
            self.thresholds = {
                "brake_distance": 10,
                "slowdown_distance": 20,
                "reroute_distance": 40
            }

        # Hybrid A* planner (used for rerouting)
        self.hybrid_astar = HybridAStar()

    def decide_action(self, vehicle_pos, obstacles, current_speed=10.0):
        """
        Decide the action based on vehicle state and obstacles.
        - vehicle_pos: (x, y)
        - obstacles: list of dicts with {"x": float, "y": float}
        - current_speed: vehicle speed in m/s
        Returns: str (BRAKE, SLOW_DOWN, KEEP_SPEED) or dict {"action": "REROUTE", "path": [...]}
        """
        for obs in obstacles:
            dx = obs["x"] - vehicle_pos[0]
            dy = obs["y"] - vehicle_pos[1]
            dist = math.hypot(dx, dy)

            if dist <= self.thresholds.get("brake_distance", 10):
                return "BRAKE"
            elif dist <= self.thresholds.get("slowdown_distance", 20):
                return "SLOW_DOWN"
            elif dist <= self.thresholds.get("reroute_distance", 40):
                # Plan new path using Hybrid A*
                print(f"[PLANNER] Vehicle {self.vehicle_id} running Hybrid A* for reroute...")
                start = (vehicle_pos[0], vehicle_pos[1])
                goal = {"x": obs["x"] + 15, "y": obs["y"] + 5}  # pick a reroute target past the obstacle
                new_path = self.hybrid_astar.plan(start, goal)
                return {"action": "REROUTE", "path": new_path}

        return "KEEP_SPEED"
