# decision_engine/motion_primitives.py
"""
Motion primitives for Hybrid A* / lattice expansion.
Generates feasible forward/reverse bicycle-model steps over a set
of discrete steering angles with simple, tunable costs.
"""

from dataclasses import dataclass
from typing import List, Tuple
import math


def wrap_to_pi(a: float) -> float:
    """Normalize angle to [-pi, pi]."""
    a = (a + math.pi) % (2.0 * math.pi) - math.pi
    return a


@dataclass
class Pose:
    x: float
    y: float
    theta: float  # heading [rad]


@dataclass
class PrimitiveResult:
    """Result of applying one primitive from a pose."""
    start: Pose
    end: Pose
    path: List[Pose]            # discretized intermediate points (start→end)
    steer: float                # steering angle [rad]
    direction: int              # +1 forward, -1 reverse
    length: float               # traveled arc length [m] (abs)
    cost: float                 # accumulated primitive cost


class MotionPrimitives:
    """
    Generates kinematically-feasible short motions using a bicycle model.
    Use expand(pose) to get successors for Hybrid A*.
    """

    def __init__(
        self,
        step_size: float = 2.0,          # meters per primitive
        wheelbase: float = 2.5,          # vehicle wheelbase [m]
        max_steer: float = 0.5,          # max steering angle [rad] (~28.6°)
        steer_samples: int = 5,          # number of discrete steering bins
        allow_reverse: bool = True,      # generate reverse motions too
        curvature_cost_weight: float = 0.3,
        reverse_cost_weight: float = 1.0,
        path_discretization: float = 0.5 # meters between waypoints in the path list
    ):
        assert steer_samples >= 1, "steer_samples must be >= 1"

        self.step_size = float(step_size)
        self.wheelbase = float(wheelbase)
        self.max_steer = float(max_steer)
        self.steer_samples = int(steer_samples)
        self.allow_reverse = bool(allow_reverse)
        self.curvature_cost_weight = float(curvature_cost_weight)
        self.reverse_cost_weight = float(reverse_cost_weight)
        self.ds_path = float(path_discretization)

        if self.steer_samples == 1:
            self._steers = [0.0]
        else:
            # Symmetric steering angles in [-max_steer, max_steer]
            self._steers = [
                -self.max_steer + i * (2 * self.max_steer / (self.steer_samples - 1))
                for i in range(self.steer_samples)
            ]

    def expand(self, pose: Pose) -> List[PrimitiveResult]:
        """
        Generate successor motions from a given pose.
        Returns a list of PrimitiveResult (both forward and optional reverse).
        """
        results: List[PrimitiveResult] = []

        # Forward motions
        for steer in self._steers:
            results.append(self._propagate(pose, steer=steer, direction=+1))

        # Reverse motions (optional)
        if self.allow_reverse:
            for steer in self._steers:
                results.append(self._propagate(pose, steer=steer, direction=-1))

        return results

    # -------------------- internals --------------------

    def _propagate(self, pose: Pose, steer: float, direction: int) -> PrimitiveResult:
        """
        Propagate bicycle model for one primitive of length 'step_size'.
        Uses small-arc integration with fixed arc-length discretization.
        """
        assert direction in (+1, -1)
        length = self.step_size * abs(direction)

        # Discretize the primitive path at ds_path resolution
        n_steps = max(1, int(math.ceil(length / self.ds_path)))
        ds = length / n_steps  # per sub-step distance

        x, y, th = pose.x, pose.y, pose.theta
        path_pts: List[Pose] = [Pose(x, y, th)]

        for _ in range(n_steps):
            # Bicycle kinematics
            dtheta = (ds / self.wheelbase) * math.tan(steer) * direction
            th_next = wrap_to_pi(th + dtheta)

            # Move along current heading (using midpoint heading for better accuracy)
            th_mid = wrap_to_pi(th + 0.5 * dtheta)
            x_next = x + (ds * direction) * math.cos(th_mid)
            y_next = y + (ds * direction) * math.sin(th_mid)

            x, y, th = x_next, y_next, th_next
            path_pts.append(Pose(x, y, th))

        end_pose = Pose(x, y, th)

        # Cost model: path length + curvature penalty + reverse penalty
        curvature_penalty = self.curvature_cost_weight * abs(steer)
        reverse_penalty = self.reverse_cost_weight if direction < 0 else 0.0
        cost = length + curvature_penalty + reverse_penalty

        return PrimitiveResult(
            start=pose,
            end=end_pose,
            path=path_pts,
            steer=steer,
            direction=direction,
            length=length,
            cost=cost
        )


# --------- minimal usage example (remove or keep for reference) ----------
if __name__ == "__main__":
    mp = MotionPrimitives(
        step_size=2.0,
        wheelbase=2.7,
        max_steer=0.6,
        steer_samples=5,
        allow_reverse=True
    )
    start = Pose(0.0, 0.0, 0.0)
    succ = mp.expand(start)
    for i, s in enumerate(succ[:6]):
        print(f"#{i}: steer={s.steer:.2f} dir={s.direction:+d} end=({s.end.x:.2f},{s.end.y:.2f},{s.end.theta:.2f}) cost={s.cost:.2f}")
