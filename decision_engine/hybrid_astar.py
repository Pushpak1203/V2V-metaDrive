# decision_engine/hybrid_astar.py

import math
import heapq


class HybridAStarPlanner:
    def __init__(self, step_size=2.0, max_steer=0.5, wheelbase=2.5):
        self.step_size = step_size
        self.max_steer = max_steer
        self.wheelbase = wheelbase

    def plan(self, start, goal, max_iter=200):
        """
        Hybrid A* simplified planner.
        - start: (x, y)
        - goal:  {"x": gx, "y": gy}
        Returns: list of (x, y) waypoints
        """
        sx, sy = start
        gx, gy = goal["x"], goal["y"]

        start_node = (0, sx, sy, 0.0, [])  # (cost, x, y, heading, path)
        open_list = []
        heapq.heappush(open_list, start_node)
        visited = set()

        for _ in range(max_iter):
            cost, x, y, theta, path = heapq.heappop(open_list)

            if (round(x), round(y)) in visited:
                continue
            visited.add((round(x), round(y)))

            # Goal check
            if math.hypot(gx - x, gy - y) < 5.0:
                return path + [(x, y)]

            # Expand neighbors (steering angles)
            for delta in [-self.max_steer, 0, self.max_steer]:
                nx = x + self.step_size * math.cos(theta)
                ny = y + self.step_size * math.sin(theta)
                ntheta = theta + (self.step_size / self.wheelbase) * math.tan(delta)

                g_cost = cost + self.step_size
                h_cost = math.hypot(gx - nx, gy - ny)
                f_cost = g_cost + h_cost

                heapq.heappush(open_list, (f_cost, nx, ny, ntheta, path + [(x, y)]))

        print("[HYBRID A*] Failed to find path within iteration limit.")
        return [(sx, sy), (gx, gy)]  # fallback straight path
