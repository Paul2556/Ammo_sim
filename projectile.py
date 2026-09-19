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
        self.side = -1

    def targeting(self, walls, projectiles, delta_time):
        if self.projectile_type == "heat_seeking_missile":
            self.angle = np.arctan2(self.vy, self.vx)
            target_found = False
            target_x = 0
            target_y = 0

            for w in walls:
                wall_center_x = w.x1 + (w.x2 - w.x1) / 2
                wall_center_y = w.y1 + (w.y2 - w.y1) / 2
                if abs( wall_center_x -self.x) < self.detection_range and abs(wall_center_y - self.y) < self.detection_range and w.heat != 0:
                    wall_Tleft_corner_angle = np.arctan2(
                        w.y1 - self.y,
                        w.x1 - self.x
                    )
                    wall_Tright_corner_angle = np.arctan2(
                        w.y1 - self.y,
                        w.x2 - self.x
                    )
                    wall_Bleft_corner_angle = np.arctan2(
                        w.y2 - self.y,
                        w.x1 - self.x
                    )
                    wall_Bright_corner_angle = np.arctan2(
                        w.y2 - self.y,
                        w.x2 - self.x
                    )
                    if (
                        abs(np.arctan2(np.sin(self.angle - wall_Tleft_corner_angle), np.cos(self.angle - wall_Tleft_corner_angle))) < self.detection_cone_angle * np.pi / 180 or
                        abs(np.arctan2(np.sin(self.angle - wall_Tright_corner_angle), np.cos(self.angle - wall_Tright_corner_angle))) < self.detection_cone_angle * np.pi / 180 or
                        abs(np.arctan2(np.sin(self.angle - wall_Bleft_corner_angle), np.cos(self.angle - wall_Bleft_corner_angle))) < self.detection_cone_angle * np.pi / 180 or
                        abs(np.arctan2(np.sin(self.angle - wall_Bright_corner_angle), np.cos(self.angle - wall_Bright_corner_angle))) < self.detection_cone_angle * np.pi / 180
                    ):
                        if np.sqrt(
                            (wall_center_x - self.x) ** 2 +
                            (wall_center_y - self.y) ** 2
                        ) < self.detection_range:
                            target_found = True
                            target_x = wall_center_x
                            target_y = wall_center_y
                            break

            if not target_found:
                for p in projectiles:
                    if p is self or p.heat == 0:
                        continue
                    if abs(p.x - self.x) < self.detection_range and abs(p.y - self.y) < self.detection_range:
                        angle_to_p = np.arctan2(p.y - self.y, p.x - self.x)
                        angle_diff = abs(np.arctan2(np.sin(self.angle - angle_to_p), np.cos(self.angle - angle_to_p)))
                        if angle_diff < self.detection_cone_angle * np.pi / 180:
                            if np.sqrt((p.x - self.x) ** 2 + (p.y - self.y) ** 2) < self.detection_range:
                                target_found = True
                                target_x = p.x
                                target_y = p.y
                                break
            
            if target_found:
                self.angle = np.arctan2(
                    target_y - self.y,
                    target_x - self.x
                )
                speed = np.sqrt(self.vx**2 + self.vy**2)
                target_vx = speed * np.cos(self.angle)
                target_vy = speed * np.sin(self.angle)
                self.vx += (target_vx - self.vx) * self.turn_rate * delta_time
                self.vy += (target_vy - self.vy) * self.turn_rate * delta_time
