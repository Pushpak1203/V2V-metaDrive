import math
import time


class VehicleManager:
    """
    Handles vehicle control in MetaDrive.
    Provides braking, slowdown, keep-speed, and Hybrid A* path following.
    """

    def __init__(self, env):
        """
        Args:
            env: MetaDrive environment (from EnvManager)
        """
        self.env = env

    def get_vehicle(self, vehicle_id):
        """Fetch the vehicle instance from the MetaDrive env."""
        if vehicle_id in self.env.vehicles:
            return self.env.vehicles[vehicle_id]
        else:
            raise RuntimeError(f"Vehicle {vehicle_id} not found in MetaDrive environment.")

    # -----------------------------
    # Basic Control Commands
    # -----------------------------
    def apply_brake(self, vehicle):
        """Apply full brake to stop vehicle quickly."""
        vehicle.set_action([0.0, -1.0])  # [steering, throttle-brake]
        print(f"[ACTION] Vehicle {vehicle.id} -> BRAKE")

    def apply_slowdown(self, vehicle, factor=0.5):
        """Reduce vehicle speed by throttling down."""
        current_speed = self._get_speed(vehicle)
        target_speed = max(current_speed * factor, 1.0)
        throttle = target_speed / max(current_speed, 1.0)
        vehicle.set_action([0.0, throttle])
        print(f"[ACTION] Vehicle {vehicle.id} -> SLOW_DOWN to {target_speed:.2f} m/s")

    def keep_speed(self, vehicle, target_throttle=0.5):
        """Maintain current cruising speed."""
        vehicle.set_action([0.0, target_throttle])
        print(f"[ACTION] Vehicle {vehicle.id} -> KEEP_SPEED at throttle {target_throttle}")

    # -----------------------------
    # Hybrid A* Path Following
    # -----------------------------
    def follow_path(self, vehicle, path, waypoint_reach_thresh=2.0, sleep_time=0.1):
        """
        Makes vehicle follow a Hybrid A* path waypoint by waypoint.

        Args:
            vehicle: MetaDrive vehicle object
            path: list of (x, y, theta) waypoints
            waypoint_reach_thresh: distance threshold to consider a waypoint reached
            sleep_time: sleep between steps (for real-time sim control)
        """
        print(f"[FOLLOW_PATH] Vehicle {vehicle.id} starting path with {len(path)} waypoints")

        for i, (x, y, theta) in enumerate(path):
            while True:
                # Get current vehicle position
                current_pos = vehicle.position  # np.array([x, y])
                dx = x - current_pos[0]
                dy = y - current_pos[1]
                distance = math.sqrt(dx**2 + dy**2)

                if distance < waypoint_reach_thresh:
                    print(f"[FOLLOW_PATH] Vehicle {vehicle.id} reached waypoint {i+1}/{len(path)}")
                    break  # Move to next waypoint

                # Steering control towards waypoint
                target_heading = math.atan2(dy, dx)
                current_heading = vehicle.heading_theta
                heading_error = self._normalize_angle(target_heading - current_heading)

                steering = max(min(heading_error, 0.5), -0.5)  # clamp [-0.5, 0.5]
                throttle = 0.4  # moderate forward speed

                vehicle.set_action([steering, throttle])
                time.sleep(sleep_time)

        print(f"[FOLLOW_PATH] Vehicle {vehicle.id} finished Hybrid A* path.")

    # -----------------------------
    # Helper Methods
    # -----------------------------
    def _get_speed(self, vehicle):
        """Return current vehicle speed (m/s)."""
        v = vehicle.velocity  # np.array([vx, vy])
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    def _normalize_angle(self, angle):
        """Wrap angle to [-pi, pi]."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle
