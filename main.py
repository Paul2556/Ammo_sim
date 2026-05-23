import arcade, numpy as np

class Projectile:

    def __init__(self, x, y, vx, vy, color=arcade.color.RED, turn_rate=0.1, projectile_type="bullet", alive=True, thrust=0, detection_range=0, detection_cone_angle=0, brightness=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.brightness = brightness
        self.detection_range = detection_range
        self.detection_cone_angle = detection_cone_angle
        self.alive = alive
        self.projectile_type = projectile_type
        self.angle = np.arctan2(vy, vx)
        self.turn_rate = turn_rate
        self.thrust = thrust
        self.trail = [(x, y, self.angle)]

class Wall:

    def __init__(self, x1, y1, x2, y2, durability, strength, color, Ricochet_Chance, Ricochet_Treshold=30, Ricochet_Loss=0.5, Ricochet_Loss_Variation=0.1, Detected=False, brightness=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.durability = durability
        self.strength = strength
        self.color = color
        self.Ricochet_Chance = Ricochet_Chance
        self.Ricochet_Treshold = Ricochet_Treshold
        self.Ricochet_Loss = Ricochet_Loss
        self.Ricochet_Loss_Variation = Ricochet_Loss_Variation
        self.detected = Detected
        self.brightness = brightness

class Game(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "Projectile")
        self.mouse_x = 0
        self.mouse_y = 0
        self.projectiles = []
        self.walls = [Wall(600, 600, 700, 700, 200, 100, arcade.color.WHITE, 0.5,brightness=1)]
        self.paused = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_x = x
        self.mouse_y = y
        if button == arcade.MOUSE_BUTTON_LEFT and not modifiers & arcade.key.MOD_SHIFT:
            global bullet_x, bullet_y
            bullet_x = x
            bullet_y = y
        if button == arcade.MOUSE_BUTTON_LEFT and modifiers & arcade.key.MOD_SHIFT:
            self.projectiles.append(Projectile(bullet_x, bullet_y,100* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)),100 * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), arcade.color.RED, projectile_type="bullet"))
        if button == arcade.MOUSE_BUTTON_RIGHT and not modifiers & arcade.key.MOD_SHIFT:
            bullet_x = x
            bullet_y = y
        if button == arcade.MOUSE_BUTTON_RIGHT and modifiers & arcade.key.MOD_SHIFT:
            self.projectiles.append(Projectile(bullet_x, bullet_y, 100* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)),100 * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), arcade.color.ORANGE, projectile_type="rocket", thrust=50))
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            for projectile in self.projectiles:
                projectile.angle = np.arctan2(y - projectile.y, x - projectile.x)
                projectile.vx = 200 * np.cos(projectile.angle)
                projectile.vy = 200 * np.sin(projectile.angle)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        if key == arcade.key.R:
            self.mouse_x = 0
            self.mouse_y = 0
            self.projectiles = []
            self.walls = [Wall(600, 600, 700, 700, 200, 100, arcade.color.WHITE, 0.5,brightness=1)]
        if key == arcade.key.H:
            self.projectiles.append(Projectile(self.mouse_x, self.mouse_y, 200, 150, arcade.color.PURPLE, projectile_type="heat_seeking_missile", detection_range=500, turn_rate=1, detection_cone_angle=28, thrust=20))
        if key == arcade.key.W and not modifiers & arcade.key.MOD_SHIFT:
            print("point a set")
            global pointa
            pointa = (self.mouse_x, self.mouse_y)
        if key == arcade.key.W and modifiers & arcade.key.MOD_SHIFT:
            print("point b set")
            global pointb
            pointb = (self.mouse_x, self.mouse_y)
            self.walls.append(Wall(pointa[0], pointa[1], pointb[0], pointb[1], 200, 100, arcade.color.WHITE, 0,brightness=1))
        if key == arcade.key.F:
            self.projectiles.append(Projectile(self.mouse_x, self.mouse_y, 200, 150, arcade.color.YELLOW, projectile_type="flare", brightness=100))

    def on_draw(self):
        self.clear()

        for wall in self.walls:
            if wall.detected:
                wall.color = arcade.color.GREEN
            else:
                wall.color = arcade.color.WHITE
            arcade.draw_lbwh_rectangle_filled(
                wall.x1,
                wall.y1,
                wall.x2 - wall.x1,
                wall.y2 - wall.y1,
                wall.color
            )
            arcade.draw_text(
                        f"{int(wall.durability)}",
                        wall.x1 + (wall.x2 - wall.x1) / 2,
                        wall.y1 + (wall.y2 - wall.y1) / 2,
                        arcade.color.BLACK,
                        20,
                        anchor_x="center",
                        anchor_y="center"
            )

        for projectile in self.projectiles:
            # Draw the trail
            for i in range(1, len(projectile.trail)):
                arcade.draw_line(
                    projectile.trail[i-1][0],
                    projectile.trail[i-1][1],
                    projectile.trail[i][0],
                    projectile.trail[i][1],
                    projectile.color,
                    2
                )
            arcade.draw_circle_filled(
                projectile.x,
                projectile.y,
                5,
                projectile.color
            )
            arcade.draw_line(
                projectile.x,
                projectile.y,
                projectile.x + projectile.vx * 0.1,
                projectile.y + projectile.vy * 0.1,
                arcade.color.GREEN,
                2
            )
            if projectile.projectile_type == "heat_seeking_missile":
                arcade.draw_line(
                    projectile.x,
                    projectile.y,
                    projectile.x + projectile.detection_range * np.cos(projectile.angle + projectile.detection_cone_angle * np.pi / 180),
                    projectile.y + projectile.detection_range * np.sin(projectile.angle + projectile.detection_cone_angle * np.pi / 180),
                    arcade.color.GREEN,
                    2
                )
                arcade.draw_line(
                    projectile.x,
                    projectile.y,
                    projectile.x + projectile.detection_range * np.cos(projectile.angle - projectile.detection_cone_angle * np.pi / 180),
                    projectile.y + projectile.detection_range * np.sin(projectile.angle - projectile.detection_cone_angle * np.pi / 180),
                    arcade.color.GREEN,
                    2
                )

    def on_update(self, delta_time):
        if self.paused:
            return
        for projectile in self.projectiles:
            if np.abs(projectile.trail[-1][2] - projectile.angle) > 0.1:
                projectile.angle = np.arctan2(projectile.vy, projectile.vx)
                projectile.trail.append((projectile.x, projectile.y, projectile.angle))
            projectile.trail.append((projectile.x, projectile.y, projectile.angle))
            if projectile.alive == False:
                self.projectiles.remove(projectile)
                continue
            if not projectile.alive or projectile.x < 0 or projectile.x > self.width or projectile.y < 0 or projectile.y > self.height:
                projectile.alive = False
                print("ammo destroyed")
                continue
            if projectile.projectile_type == "flare":
                projectile.color = (projectile.color[0], projectile.color[1], projectile.color[2], int(projectile.brightness * 2.55))
                #! Put flare priority and targeting code here soon ;-;
                projectile.brightness -= 1
                if projectile.brightness <= 0:
                    projectile.alive = False
                    print("flare expired")
                    continue
            projectile.vx += projectile.thrust * np.cos(projectile.angle) * delta_time
            projectile.vy += projectile.thrust * np.sin(projectile.angle) * delta_time
            projectile.x += projectile.vx * delta_time
            projectile.y += projectile.vy * delta_time
            
            drag = 0.001 * np.sqrt(projectile.vx**2 + projectile.vy**2)
            projectile.vx -= drag * projectile.vx * delta_time
            projectile.vy -= drag * projectile.vy * delta_time

            for wall in self.walls:
                # ---------------- GUIDANCE PHASE ----------------

                if projectile.projectile_type == "heat_seeking_missile":
                    projectile.angle = np.arctan2(projectile.vy, projectile.vx)

                    target_found = False
                    target_x = 0
                    target_y = 0

                    for wall in self.walls:

                        wall_center_x = wall.x1 + (wall.x2 - wall.x1) / 2
                        wall_center_y = wall.y1 + (wall.y2 - wall.y1) / 2

                        wall_Tleft_corner_angle = np.arctan2(
                            wall.y1 - projectile.y,
                            wall.x1 - projectile.x
                        )

                        wall_Tright_corner_angle = np.arctan2(
                            wall.y1 - projectile.y,
                            wall.x2 - projectile.x
                        )

                        wall_Bleft_corner_angle = np.arctan2(
                            wall.y2 - projectile.y,
                            wall.x1 - projectile.x
                        )

                        wall_Bright_corner_angle = np.arctan2(
                            wall.y2 - projectile.y,
                            wall.x2 - projectile.x
                        )

                        if (
                            abs(np.arctan2(np.sin(projectile.angle - wall_Tleft_corner_angle), np.cos(projectile.angle - wall_Tleft_corner_angle))) < projectile.detection_cone_angle * np.pi / 180 or
                            abs(np.arctan2(np.sin(projectile.angle - wall_Tright_corner_angle), np.cos(projectile.angle - wall_Tright_corner_angle))) < projectile.detection_cone_angle * np.pi / 180 or
                            abs(np.arctan2(np.sin(projectile.angle - wall_Bleft_corner_angle), np.cos(projectile.angle - wall_Bleft_corner_angle))) < projectile.detection_cone_angle * np.pi / 180 or
                            abs(np.arctan2(np.sin(projectile.angle - wall_Bright_corner_angle), np.cos(projectile.angle - wall_Bright_corner_angle))) < projectile.detection_cone_angle * np.pi / 180
                        ):

                            if np.sqrt(
                                (wall_center_x - projectile.x) ** 2 +
                                (wall_center_y - projectile.y) ** 2
                            ) < projectile.detection_range:

                                target_found = True
                                target_x = wall_center_x
                                target_y = wall_center_y

                                break

                    if target_found:

                        projectile.angle = np.arctan2(
                            target_y - projectile.y,
                            target_x - projectile.x
                        )

                        speed = np.sqrt(projectile.vx**2 + projectile.vy**2)

                        target_vx = speed * np.cos(projectile.angle)
                        target_vy = speed * np.sin(projectile.angle)

                        projectile.vx += (target_vx - projectile.vx) * projectile.turn_rate * delta_time
                        projectile.vy += (target_vy - projectile.vy) * projectile.turn_rate * delta_time


                # ---------------- COLLISION PHASE ----------------

                for wall in self.walls:

                    if (
                        wall.x1 <= projectile.x <= wall.x2
                        and
                        wall.y1 <= projectile.y <= wall.y2
                    ):

                        mx = np.sqrt(projectile.vx**2 + projectile.vy**2)

                        wall.durability -= .1 * mx * delta_time

                        if wall.durability <= 0:
                            self.walls.remove(wall)
                            print("wall destroyed")
                            break

                        else:

                            if np.random.random() < wall.Ricochet_Chance:

                                projectile.color = arcade.color.YELLOW

                                if projectile.x - wall.x1 < .3 * (wall.x2 - wall.x1):

                                    projectile.vx = -projectile.vx * (
                                        wall.Ricochet_Loss +
                                        np.random.uniform(
                                            -wall.Ricochet_Loss_Variation,
                                            wall.Ricochet_Loss_Variation
                                        )
                                    )

                                    projectile.angle = np.arctan2(
                                        projectile.vy,
                                        projectile.vx
                                    )

                                    if wall.x2 - projectile.x < .3 * (wall.x2 - wall.x1):
                                        projectile.x = wall.x2 + 1
                                    else:
                                        projectile.x = wall.x1 - 1

                                elif projectile.y - wall.y1 < .3 * (wall.y2 - wall.y1):

                                    projectile.vy = -projectile.vy * (
                                        wall.Ricochet_Loss +
                                        np.random.uniform(
                                            -wall.Ricochet_Loss_Variation,
                                            wall.Ricochet_Loss_Variation
                                        )
                                    )

                                    projectile.angle = np.arctan2(
                                        projectile.vy,
                                        projectile.vx
                                    )

                                    if wall.y2 - projectile.y < .3 * (wall.y2 - wall.y1):
                                        projectile.y = wall.y2 + 1
                                    else:
                                        projectile.y = wall.y1 - 1

                                print("ammo rico")

                            else:
                                projectile.alive = False

                        if mx < wall.strength:
                            projectile.alive = False
                            break

                        break

game = Game()
arcade.run()