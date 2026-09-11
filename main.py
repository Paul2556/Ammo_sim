"""
Projectile Simulation
This code simulates the behavior of projectiles (bullets, rockets, heat-seeking missiles, and flares) in a 2D environment with walls. The projectiles are affected by gravity, drag, and can interact with walls by either damaging them or ricocheting off of them. The simulation also includes a visual representation of the projectiles and their trails, as well as the walls and their durability.
This goes by 10 pixels per meter, so a projectile with a speed of 1000 pixels per second is equivalent to a speed of 100 meters per second in real life. The simulation also includes a heat mechanic, where projectiles and walls can emit heat that can be detected by heat-seeking missiles. The heat is visualized as a yellow circle around the projectile or wall, with the intensity of the color representing the amount of heat. The simulation can be paused and reset using the spacebar and R key, respectively. The user can also spawn different types of projectiles using the mouse buttons and the H and F keys.
"""
import config
import arcade, numpy as np
import projectile, wall

# Constants
average_bullet_speed = 1000 #default 1000
average_rocket_speed = 800 #default 800
gravity = 9.81 #default 9.81
heat_visibility_multiplier = 1 #default 2.55, higher values make heat more visible but also make it more opaque, lower values make it less visible but also more transparent
angle_update_interval = 10 #default 10, higher values make the trail update less frequently but also make it less accurate, lower values make the trail update more frequently but also make it more accurate
fade_rate = 5 #default 5, higher values make the trail fade faster but also make it more transparent, lower values make the trail fade slower but also make it more visible
trail_length = 100 #default 100, higher values make the trail longer but also make it more performance intensive, lower values make the trail shorter but also make it less visible 
air_density = .001 #default 0.001, higher values make the projectiles slow down faster but also make them more affected by drag, lower values make the projectiles slow down slower but also make them less affected by drag

bullet_x = 0
bullet_y = 0

class Game(arcade.Window):

    def __init__(self):
        super().__init__(1280, 720, "Kill Tofu Simulator")
        self.mouse_x = 0
        self.mouse_y = 0
        self.projectiles = []
        self.walls = [wall.Wall(self.width//2-50, self.height//2-50, self.width//2+50, self.height//2+50, 200, 100, arcade.color.WHITE, 1,heat=1)]
        self.paused = False
    
    def projectile_spawner(self, key, hotkey, modifiers, color=arcade.color.RED, turn_rate=0.1, projectile_type="bullet", thrust=0, detection_range=0, detection_cone_angle=0, heat=0):
        if key == hotkey and not modifiers & arcade.key.MOD_SHIFT:
            global bullet_x, bullet_y
            bullet_x = self.mouse_x
            bullet_y = self.mouse_y
        if key == hotkey and modifiers & arcade.key.MOD_SHIFT:
            self.projectiles.append(projectile.Projectile(bullet_x, bullet_y, average_bullet_speed* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), average_bullet_speed * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), color=color, turn_rate=turn_rate, projectile_type=projectile_type, heat=heat, thrust=thrust, detection_cone_angle=detection_cone_angle, detection_range=detection_range))
    
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
            for proj in self.projectiles:
                proj.angle = np.arctan2(self.mouse_y - proj.y, self.mouse_x - proj.x)
                proj.vx = 200 * np.cos(proj.angle)
                proj.vy = 200 * np.sin(proj.angle)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        if key == arcade.key.R:
            self.mouse_x = 0
            self.mouse_y = 0
            self.projectiles = []
            self.walls = [wall.Wall(self.width//2-50, self.height//2-50, self.width//2+50, self.height//2+50, 200, 100, arcade.color.WHITE, 1,heat=1)]
        self.projectile_spawner(key, arcade.key.B, modifiers, color=arcade.color.RED, projectile_type="bullet", heat=50)
        self.projectile_spawner(key, arcade.key.O, modifiers, color=arcade.color.ORANGE, projectile_type="rocket", thrust=10, heat=100)
        self.projectile_spawner(key, arcade.key.H, modifiers, 
                                color=arcade.color.PURPLE, 
                                turn_rate=1, 
                                projectile_type="heat_seeking_missile", 
                                heat=100, 
                                detection_cone_angle=45, 
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
            self.walls.append(wall.Wall(pointax, pointay, pointbx, pointby, 
                                durability=200, 
                                strength=100, 
                                color=arcade.color.WHITE, 
                                Ricochet_Chance=0,
                                heat=1
                            )
                        )
            if swapped_x:
                pointax, pointbx = pointbx, pointax
                swapped_x = False
            if swapped_y:
                pointay, pointby = pointby, pointay
                swapped_y = False
        self.projectile_spawner(key, arcade.key.F, modifiers, 
                                color=arcade.color.YELLOW, 
                                projectile_type="flare", 
                                heat=100
                            )

    #$ END OF SPAWNING STUFF
    def on_draw(self):
        self.clear()
        arcade.draw_circle_filled(
                    bullet_x,
                    bullet_y,
                    3,
                    (255, 255, 255)
                )
        for w in self.walls:
            if w.heat > 0:
                arcade.draw_circle_filled(
                    w.x1 + (w.x2 - w.x1) / 2,
                    w.y1 + (w.y2 - w.y1) / 2,
                    w.heat*heat_visibility_multiplier,
                    (255, 255, 0, int(w.heat * (heat_visibility_multiplier/3)))
                )
            if w.detected:
                w.color = arcade.color.GREEN
            else:
                w.color = arcade.color.WHITE
            arcade.draw_lbwh_rectangle_filled(
                w.x1,
                w.y1,
                w.x2 - w.x1,
                w.y2 - w.y1,
                w.color
            )
            arcade.draw_text(
                        f"{int(w.durability)}",
                        w.x1 + (w.x2 - w.x1) / 2,
                        w.y1 + (w.y2 - w.y1) / 2,
                        arcade.color.BLACK,
                        20,
                        anchor_x="center",
                        anchor_y="center"
            )

        for proj in self.projectiles:
            if proj.heat > 0:
                arcade.draw_circle_filled(
                    proj.x,
                    proj.y,
                    proj.heat*heat_visibility_multiplier,
                    (255, 255, 0, int(proj.heat * (heat_visibility_multiplier/3)))
                )
            # Draw the trail
            for i in range(1, len(proj.trail)):
                if proj.trail[i-1][3] < 0:
                    arcade.draw_line(
                    proj.trail[i-1][0],
                    proj.trail[i-1][1],
                    proj.trail[i][0],
                    proj.trail[i][1],
                    (proj.color[0], proj.color[1], proj.color[2], 0),
                    2
                    )   
                elif proj.projectile_type == "flare":     
                    arcade.draw_line(
                        proj.trail[i-1][0],
                        proj.trail[i-1][1],
                        proj.trail[i][0],
                        proj.trail[i][1],
                        (proj.color[0], proj.color[1], proj.color[2], proj.heat * heat_visibility_multiplier),
                        2
                    )        
                else:
                    arcade.draw_line(
                        proj.trail[i-1][0],
                        proj.trail[i-1][1],
                        proj.trail[i][0],
                        proj.trail[i][1],
                        (proj.color[0], proj.color[1], proj.color[2], int(proj.trail[i-1][3])),
                        2
                    )
            arcade.draw_circle_filled(
                proj.x,
                proj.y,
                5,
                proj.color
            ) 
            arcade.draw_line(
                proj.x,
                proj.y,
                proj.x + proj.vx * 0.1,
                proj.y + proj.vy * 0.1,
                arcade.color.GREEN,
                2
            )
            if proj.projectile_type == "heat_seeking_missile":
                arcade.draw_line(
                    proj.x,
                    proj.y,
                    proj.x + proj.detection_range * np.cos(proj.angle + proj.detection_cone_angle * np.pi / 180),
                    proj.y + proj.detection_range * np.sin(proj.angle + proj.detection_cone_angle * np.pi / 180),
                    arcade.color.GREEN,
                    2
                )
                arcade.draw_line(
                    proj.x,
                    proj.y,
                    proj.x + proj.detection_range * np.cos(proj.angle - proj.detection_cone_angle * np.pi / 180),
                    proj.y + proj.detection_range * np.sin(proj.angle - proj.detection_cone_angle * np.pi / 180),
                    arcade.color.GREEN,
                    2
                )

    def on_update(self, delta_time):
        if self.paused:
            return
        for proj in self.projectiles:
            # print(len(proj.trail), proj.trail[0][3])
            if np.abs(proj.trail[-1][2] - proj.angle) > 0.1 or np.mod(len(proj.trail), angle_update_interval) == 0: #$ TRAIL AND ANGLE UPDATE
                proj.angle = np.arctan2(proj.vy, proj.vx)
                proj.trail.append((proj.x, proj.y, proj.angle, 255))
            proj.trail.append((proj.x, proj.y, proj.angle, 255))
            if proj.projectile_type != "flare":
                if proj.lazy and proj.trail_length != 50:
                    proj.trail_length = 50
                    # print("ts")
                if len(proj.trail) > proj.trail_length:
                    for i in range(len(proj.trail) - proj.trail_length):
                        proj.trail[i] = (proj.trail[i][0], proj.trail[i][1], proj.trail[i][2], proj.trail[i][3] - (fade_rate * delta_time*100))
                if proj.trail[0][3] <= 0:
                    proj.trail.pop(0)
            if proj.alive == False:
                self.projectiles.remove(proj)
                continue
            if proj.x < 0 or proj.x > self.width or proj.y < 0 or proj.y > self.height:
                if not proj.lazy:
                    proj.lazy = True
                    # print("lazy ahh")
                    continue
            if proj.x < 0-(2*proj.trail_length+average_bullet_speed) or proj.x > self.width+(2*proj.trail_length+average_bullet_speed) or proj.y < 0-(2*proj.trail_length+average_bullet_speed) or proj.y > self.height+(2*proj.trail_length+average_bullet_speed):
                proj.alive = False
                print("ammo destroyed")
                continue
            if proj.projectile_type == "flare":
                proj.color = (proj.color[0], proj.color[1], proj.color[2], int(proj.heat * 2.55))
                proj.heat -= 1
                if proj.heat <= 0:
                    proj.alive = False
                    print("flare expired")
                    continue
                if len(proj.trail) > 5:
                    for i in range(len(proj.trail) - 3):
                        proj.trail[i] = (proj.trail[i][0], proj.trail[i][1], proj.trail[i][2], proj.trail[i][3] * .2 - .01)
                if proj.trail[0][3] <= 0:
                    proj.trail.pop(0)
            proj.vx += proj.thrust * np.cos(proj.angle) * delta_time
            proj.vy += proj.thrust * np.sin(proj.angle) * delta_time
            proj.x += proj.vx * delta_time
            proj.y += proj.vy * delta_time
            if not proj.lazy:
                drag = air_density * np.sqrt(proj.vx**2 + proj.vy**2)
                proj.vy -= gravity * delta_time
                proj.vx -= drag * proj.vx * delta_time
                proj.vy -= drag * proj.vy * delta_time

                for w in self.walls:
                    if proj.projectile_type == "heat_seeking_missile":
                        proj.angle = np.arctan2(proj.vy, proj.vx)
                        target_found = False
                        target_x = 0
                        target_y = 0

                        for w in self.walls:
                            wall_center_x = w.x1 + (w.x2 - w.x1) / 2
                            wall_center_y = w.y1 + (w.y2 - w.y1) / 2
                            if abs( wall_center_x -proj.x) < proj.detection_range and abs(wall_center_y - proj.y) < proj.detection_range:
                                wall_Tleft_corner_angle = np.arctan2(
                                    w.y1 - proj.y,
                                    w.x1 - proj.x
                                )
                                wall_Tright_corner_angle = np.arctan2(
                                    w.y1 - proj.y,
                                    w.x2 - proj.x
                                )
                                wall_Bleft_corner_angle = np.arctan2(
                                    w.y2 - proj.y,
                                    w.x1 - proj.x
                                )
                                wall_Bright_corner_angle = np.arctan2(
                                    w.y2 - proj.y,
                                    w.x2 - proj.x
                                )
                                if (
                                    abs(np.arctan2(np.sin(proj.angle - wall_Tleft_corner_angle), np.cos(proj.angle - wall_Tleft_corner_angle))) < proj.detection_cone_angle * np.pi / 180 or
                                    abs(np.arctan2(np.sin(proj.angle - wall_Tright_corner_angle), np.cos(proj.angle - wall_Tright_corner_angle))) < proj.detection_cone_angle * np.pi / 180 or
                                    abs(np.arctan2(np.sin(proj.angle - wall_Bleft_corner_angle), np.cos(proj.angle - wall_Bleft_corner_angle))) < proj.detection_cone_angle * np.pi / 180 or
                                    abs(np.arctan2(np.sin(proj.angle - wall_Bright_corner_angle), np.cos(proj.angle - wall_Bright_corner_angle))) < proj.detection_cone_angle * np.pi / 180
                                ):
                                    if np.sqrt(
                                        (wall_center_x - proj.x) ** 2 +
                                        (wall_center_y - proj.y) ** 2
                                    ) < proj.detection_range:
                                        target_found = True
                                        target_x = wall_center_x
                                        target_y = wall_center_y
                                        break
                        if target_found:
                            proj.angle = np.arctan2(
                                target_y - proj.y,
                                target_x - proj.x
                            )
                            speed = np.sqrt(proj.vx**2 + proj.vy**2)
                            target_vx = speed * np.cos(proj.angle)
                            target_vy = speed * np.sin(proj.angle)
                            proj.vx += (target_vx - proj.vx) * proj.turn_rate * delta_time
                            proj.vy += (target_vy - proj.vy) * proj.turn_rate * delta_time
                    if (
                            w.x1 <= proj.x <= w.x2
                            and
                            w.y1 <= proj.y <= w.y2
                    ):
                        mx = np.sqrt(proj.vx**2 + proj.vy**2)
                        w.durability -= .1 * mx * delta_time
                        if w.durability <= 0:
                            self.walls.remove(w)
                            print("wall destroyed")
                            break
                        else: #$ RECCOCHET
                            if np.random.random() < w.Ricochet_Chance:
                                #TODO: Have to redo this whole thing
                                proj.color = arcade.color.YELLOW
                                if proj.x - w.x1 < .2 * (w.x2 - w.x1):
                                    proj.vx = -proj.vx * (
                                        w.Ricochet_Loss +
                                        np.random.uniform(
                                            -w.Ricochet_Loss_Variation,
                                            w.Ricochet_Loss_Variation
                                        )
                                    )
                                    proj.angle = np.arctan2(
                                        proj.vy,
                                        proj.vx
                                    )
                                    if w.x2 - proj.x < .2 * (w.x2 - w.x1):
                                        proj.x = w.x2 + 1
                                    else:
                                        proj.x = w.x1 - 1
                                elif proj.y - w.y1 < .2 * (w.y2 - w.y1):
                                    proj.vy = -proj.vy * (
                                        w.Ricochet_Loss +
                                        np.random.uniform(
                                            -w.Ricochet_Loss_Variation,
                                            w.Ricochet_Loss_Variation
                                        )
                                    )
                                    proj.angle = np.arctan2(
                                        proj.vy,
                                        proj.vx
                                    )
                                    if w.y2 - proj.y < .2 * (w.y2 - w.y1):
                                        proj.y = w.y2 + 1
                                    else:
                                        proj.y = w.y1 - 1
                                print("ammo rico")
                            else:
                                proj.alive = False
                        if mx < w.strength:
                            proj.alive = False
                            break
                        break

game = Game()
arcade.run()