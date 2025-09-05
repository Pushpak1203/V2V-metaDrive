# decision_engine/response_planner.py

import yaml
from decision_engine.hybrid_astar import HybridAStarPlanner


class ResponsePlanner:
    def __init__(self, vehicle_id, config_path="config/thresholds.yaml"):
        self.vehicle_id = vehicle_id

        # Load thresholds from config
        with open(config_path, "r") as f:
            self.thresholds = yaml.safe_load(f)

        # Hybrid A* planner (used for rerouting)
        self.hybrid_astar = HybridAStarPlanner()

    def decide_action(self, vehicle_pos, obstacles, current_speed=10.0):
        """
        Decide the action based on vehicle state and obstacles.
        - vehicle_pos: (x, y)
        - obstacles: list of dicts with {"x": float, "y": float}
        - current_speed: vehicle speed in m/s
        """
        for obs in obstacles:
            dx = obs["x"] - vehicle_pos[0]
            dy = obs["y"] - vehicle_pos[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist <= self.thresholds["brake_distance"]:
                return "BRAKE"
            elif dist <= self.thresholds["slowdown_distance"]:
                return "SLOW_DOWN"
            elif dist <= self.thresholds["reroute_distance"]:
                # Plan new path using Hybrid A*
                print(f"[PLANNER] Vehicle {self.vehicle_id} running Hybrid A* for reroute...")
                new_path = self.hybrid_astar.plan(vehicle_pos, obs)
                return {"action": "REROUTE", "path": new_path}

        return "KEEP_SPEED"
