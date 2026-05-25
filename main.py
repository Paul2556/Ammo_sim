import arcade, numpy as np


# Constants
average_bullet_speed = 1000 #default 1000
average_rocket_speed = 800 #default 800
gravity = 100 #default 9.81
heat_visibility_multiplier = 1 #default 2.55, higher values make heat more visible but also make it more opaque, lower values make it less visible but also more transparent
angle_update_interval = 10 #default 10, higher values make the trail update less frequently but also make it less accurate, lower values make the trail update more frequently but also make it more accurate
fade_rate = 5 #default 5, higher values make the trail fade faster but also make it more transparent, lower values make the trail fade slower but also make it more visible
trail_length = 300 #default 100, higher values make the trail longer but also make it more performance intensive, lower values make the trail shorter but also make it less visible 
air_density = .001 #default 0.001, higher values make the projectiles slow down faster but also make them more affected by drag, lower values make the projectiles slow down slower but also make them less affected by drag
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
        self.trail_length = trail_length
    

class Wall:

    def __init__(self, x1, y1, x2, y2, durability, strength, color, Ricochet_Chance, Ricochet_Treshold=30, Ricochet_Loss=0.5, Ricochet_Loss_Variation=0.1, Detected=False, heat=0):
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
        self.heat = heat

class Game(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "Projectile")
        self.mouse_x = 0
        self.mouse_y = 0
        self.projectiles = []
        self.walls = [Wall(600, 600, 700, 700, 200, 100, arcade.color.WHITE, 1,heat=1)]
        self.paused = False
    
    def projectile_spawner(self, key, hotkey, modifiers, color=arcade.color.RED, turn_rate=0.1, projectile_type="bullet", thrust=0, detection_range=0, detection_cone_angle=0, heat=0):
        if key == hotkey and not modifiers & arcade.key.MOD_SHIFT:
            global bullet_x, bullet_y
            bullet_x = self.mouse_x
            bullet_y = self.mouse_y
        if key == hotkey and modifiers & arcade.key.MOD_SHIFT:
            self.projectiles.append(Projectile(bullet_x, bullet_y, average_bullet_speed* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), average_bullet_speed * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), color=color, turn_rate=turn_rate, projectile_type=projectile_type, heat=heat, thrust=thrust, detection_cone_angle=detection_cone_angle, detection_range=detection_range))
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
    #$ START OF SPAWNING STUFF
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_x = x
        self.mouse_y = y
        self.projectile_spawner(button, arcade.MOUSE_BUTTON_LEFT, modifiers, color=arcade.color.RED, projectile_type="bullet", heat=50)
        self.projectile_spawner(button, arcade.MOUSE_BUTTON_RIGHT, modifiers, color=arcade.color.ORANGE, projectile_type="rocket", thrust=10, heat=100)
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            for projectile in self.projectiles:
                projectile.angle = np.arctan2(self.mouse_y - projectile.y, self.mouse_x - projectile.x)
                projectile.vx = 200 * np.cos(projectile.angle)
                projectile.vy = 200 * np.sin(projectile.angle)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        if key == arcade.key.R:
            self.mouse_x = 0
            self.mouse_y = 0
            self.projectiles = []
            self.walls = [Wall(600, 600, 700, 700, 200, 100, arcade.color.WHITE, 1,heat=1)]
        self.projectile_spawner(key, arcade.key.H, modifiers, 
                                color=arcade.color.PURPLE, 
                                turn_rate=1.5, 
                                projectile_type="heat_seeking_missile", 
                                heat=100, 
                                detection_cone_angle=180, 
                                detection_range=300,
                                thrust=40
                            )
        if key == arcade.key.W and not modifiers & arcade.key.MOD_SHIFT:
            print("point a set")
            global pointax, pointay
            pointax,pointay = self.mouse_x, self.mouse_y
        if key == arcade.key.W and modifiers & arcade.key.MOD_SHIFT:
            print("point b set")
            global pointbx, pointby, swapped_x, swapped_y
            pointbx,pointby = self.mouse_x, self.mouse_y
            if pointbx < pointax or pointby < pointay:
                if pointbx < pointax:
                    pointax, pointbx = pointbx, pointax
                    swapped_x = True
                if pointby < pointay:
                    pointay, pointby = pointby, pointay
                    swapped_y = True
            self.walls.append(Wall(pointax, pointay, pointbx, pointby, 
                                   durability=200, 
                                   strength=100, 
                                   color=arcade.color.WHITE, 
                                   Ricochet_Chance=0,
                                   heat=1))
            if swapped_x:
                pointax, pointbx = pointbx, pointax
                swapped_x = False
            if swapped_y:
                pointay, pointby = pointby, pointay
                swapped_y = False
        self.projectile_spawner(key, arcade.key.F, modifiers, color=arcade.color.YELLOW, projectile_type="flare", heat=100)

    #$ END OF SPAWNING STUFF
    def on_draw(self):
        self.clear()

        for wall in self.walls:
            if wall.heat > 0:
                arcade.draw_circle_filled(
                    wall.x1 + (wall.x2 - wall.x1) / 2,
                    wall.y1 + (wall.y2 - wall.y1) / 2,
                    wall.heat*heat_visibility_multiplier,
                    (255, 255, 0, int(wall.heat * (heat_visibility_multiplier/3)))
                )
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
            if projectile.heat > 0:
                arcade.draw_circle_filled(
                    projectile.x,
                    projectile.y,
                    projectile.heat*heat_visibility_multiplier,
                    (255, 255, 0, int(projectile.heat * (heat_visibility_multiplier/3)))
                )
            # Draw the trail
            for i in range(1, len(projectile.trail)):
                if projectile.trail[i-1][3] < 0:
                    arcade.draw_line(
                    projectile.trail[i-1][0],
                    projectile.trail[i-1][1],
                    projectile.trail[i][0],
                    projectile.trail[i][1],
                    (projectile.color[0], projectile.color[1], projectile.color[2], 0),
                    2
                    )   
                elif projectile.projectile_type == "flare":     
                    arcade.draw_line(
                        projectile.trail[i-1][0],
                        projectile.trail[i-1][1],
                        projectile.trail[i][0],
                        projectile.trail[i][1],
                        (projectile.color[0], projectile.color[1], projectile.color[2], projectile.heat * heat_visibility_multiplier),
                        2
                    )        
                else:
                    arcade.draw_line(
                        projectile.trail[i-1][0],
                        projectile.trail[i-1][1],
                        projectile.trail[i][0],
                        projectile.trail[i][1],
                        (projectile.color[0], projectile.color[1], projectile.color[2], int(projectile.trail[i-1][3])),
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
            # print(len(projectile.trail), projectile.trail[0][3])
            if np.abs(projectile.trail[-1][2] - projectile.angle) > 0.1 or np.mod(len(projectile.trail), angle_update_interval) == 0: #$ TRAIL AND ANGLE UPDATE
                projectile.angle = np.arctan2(projectile.vy, projectile.vx)
                projectile.trail.append((projectile.x, projectile.y, projectile.angle, 255))
            projectile.trail.append((projectile.x, projectile.y, projectile.angle, 255))
            if projectile.projectile_type != "flare":
                if projectile.lazy and projectile.trail_length != 50:
                    projectile.trail_length = 50
                    print("ts")
                if len(projectile.trail) > projectile.trail_length:
                    for i in range(len(projectile.trail) - projectile.trail_length):
                        projectile.trail[i] = (projectile.trail[i][0], projectile.trail[i][1], projectile.trail[i][2], projectile.trail[i][3] - (fade_rate * delta_time*100))
                if projectile.trail[0][3] <= 0:
                    projectile.trail.pop(0)
            if projectile.alive == False:
                self.projectiles.remove(projectile)
                continue
            if projectile.x < 0 or projectile.x > self.width or projectile.y < 0 or projectile.y > self.height:
                if not projectile.lazy:
                    projectile.lazy = True
                    # print("lazy ahh")
                    continue
            if projectile.x < 0-(2*projectile.trail_length+average_bullet_speed) or projectile.x > self.width+(2*projectile.trail_length+average_bullet_speed) or projectile.y < 0-(2*projectile.trail_length+average_bullet_speed) or projectile.y > self.height+(2*projectile.trail_length+average_bullet_speed):
                projectile.alive = False
                print("ammo destroyed")
                continue
            if projectile.projectile_type == "flare":
                projectile.color = (projectile.color[0], projectile.color[1], projectile.color[2], int(projectile.heat * 2.55))
                projectile.heat -= 1
                if projectile.heat <= 0:
                    projectile.alive = False
                    print("flare expired")
                    continue
                if len(projectile.trail) > 5:
                    for i in range(len(projectile.trail) - 3):
                        projectile.trail[i] = (projectile.trail[i][0], projectile.trail[i][1], projectile.trail[i][2], projectile.trail[i][3] * .2 - .01)
                if projectile.trail[0][3] <= 0:
                    projectile.trail.pop(0)
            projectile.vx += projectile.thrust * np.cos(projectile.angle) * delta_time
            projectile.vy += projectile.thrust * np.sin(projectile.angle) * delta_time
            projectile.x += projectile.vx * delta_time
            projectile.y += projectile.vy * delta_time
            if not projectile.lazy:
                drag = air_density * np.sqrt(projectile.vx**2 + projectile.vy**2)
                projectile.vy -= gravity * delta_time
                projectile.vx -= drag * projectile.vx * delta_time
                projectile.vy -= drag * projectile.vy * delta_time

                for wall in self.walls:
                    if projectile.projectile_type == "heat_seeking_missile":
                        projectile.angle = np.arctan2(projectile.vy, projectile.vx)
                        target_found = False
                        target_x = 0
                        target_y = 0

                        for wall in self.walls:
                            wall_center_x = wall.x1 + (wall.x2 - wall.x1) / 2
                            wall_center_y = wall.y1 + (wall.y2 - wall.y1) / 2
                            if abs( wall_center_x -projectile.x) < projectile.detection_range and abs(wall_center_y - projectile.y) < projectile.detection_range:
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
                        else: #$ RECCOCHET
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