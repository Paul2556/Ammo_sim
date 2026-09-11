import arcade, config, numpy as np

class Projectile:

    def __init__(self, x, y, vx, vy, color=arcade.color.RED, turn_rate=0.1, projectile_type="bullet", alive=True, thrust=0, detection_range=0, detection_cone_angle=0, heat=0, lazy=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.heat = heat
        self.detection_range = detection_range
        self.detection_cone_angle = detection_cone_angle
        self.alive = alive
        self.projectile_type = projectile_type
        self.angle = np.arctan2(vy, vx)
        self.turn_rate = turn_rate
        self.thrust = thrust
        self.trail = [(x, y, self.angle, 255)]
        self.lazy = lazy
        self.trail_length = config.trail_length