"""
Projectile Simulation
This code simulates the behavior of projectiles (bullets, rockets, heat-seeking missiles, and flares) in a 2D environment with walls. The projectiles are affected by gravity, drag, and can interact with walls by either damaging them or ricocheting off of them. The simulation also includes a visual representation of the projectiles and their trails, as well as the walls and their durability.
This goes by 10 pixels per meter, so a projectile with a speed of 1000 pixels per second is equivalent to a speed of 100 meters per second in real life. The simulation also includes a heat mechanic, where projectiles and walls can emit heat that can be detected by heat-seeking missiles. The heat is visualized as a yellow circle around the projectile or wall, with the intensity of the color representing the amount of heat. The simulation can be paused and reset using the spacebar and R key, respectively. The user can also spawn different types of projectiles using the mouse buttons and the H and F keys.
"""

from config import *
import projectile
import wall
import arcade, numpy as np
from time import sleep
from arcade.clock import GLOBAL_CLOCK


bullet_x = 0
bullet_y = 0

def clamp_alpha(a):
    return max(0, min(255, int(a)))
    
class Game(arcade.Window):
    def __init__(self):
        super().__init__(1280, 720, "Kill Tofu Simulator")
        self.held_keys = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.projectiles = []
        self.walls = [wall.Wall(self.width//2-50, self.height//2-50, self.width//2+50, self.height//2+50, 200, 100, arcade.color.WHITE, 1,heat=30)]
        self.paused = False
    
    def reset(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.projectiles = []
        self.walls = [wall.Wall(self.width//2-50, self.height//2-50, self.width//2+50, self.height//2+50, 200, 100, arcade.color.WHITE, 1,heat=30)]
    def shift_held(self):
        return arcade.key.LSHIFT in self.held_keys or arcade.key.RSHIFT in self.held_keys

    def projectile_spawner(self, hotkey, delta_time, color=arcade.color.RED, turn_rate=0.1, projectile_type="bullet", thrust=0, detection_range=0, detection_cone_angle=0, heat=0, fire_rate=0.1, automatic=True):
        if hotkey not in self.held_keys:
            return
        global bullet_x, bullet_y
        if self.shift_held() and automatic:
            if GLOBAL_CLOCK.time % fire_rate < delta_time:
                self.projectiles.append(projectile.Projectile(bullet_x, bullet_y, average_bullet_speed* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), average_bullet_speed * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), color=color, turn_rate=turn_rate, projectile_type=projectile_type, heat=heat, thrust=thrust, detection_cone_angle=detection_cone_angle, detection_range=detection_range))
        elif not automatic:
            self.projectiles.append(projectile.Projectile(bullet_x, bullet_y, average_bullet_speed* np.cos(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), average_bullet_speed * np.sin(np.arctan2(self.mouse_y - bullet_y, self.mouse_x - bullet_x)), color=color, turn_rate=turn_rate, projectile_type=projectile_type, heat=heat, thrust=thrust, detection_cone_angle=detection_cone_angle, detection_range=detection_range))
            self.held_keys.remove(hotkey)
        else:
            bullet_x = self.mouse_x
            bullet_y = self.mouse_y

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    #$ START OF SPAWNING STUFF
    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_x = x
        self.mouse_y = y
        self.held_keys.add(button)

    def on_mouse_release(self, x, y, button, modifiers):
        self.held_keys.discard(button)
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            for proj in self.projectiles:
                proj.angle = np.arctan2(self.mouse_y - proj.y, self.mouse_x - proj.x)
                proj.vx = 200 * np.cos(proj.angle)
                proj.vy = 200 * np.sin(proj.angle)

    def on_key_press(self, key, modifiers):
        self.held_keys.add(key)
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        if key == arcade.key.R:
            self.reset()
        if key == arcade.key.W and not modifiers & arcade.key.MOD_SHIFT:
            print("point a set")
            global pointax, pointay
            pointax,pointay = self.mouse_x, self.mouse_y
        if key == arcade.key.W and modifiers & arcade.key.MOD_SHIFT:
            print("point b set")
            global pointbx, pointby
            pointbx, pointby = self.mouse_x, self.mouse_y
            pointax, pointbx = min(pointax, pointbx), max(pointax, pointbx)
            pointay, pointby = min(pointay, pointby), max(pointay, pointby)
            self.walls.append(wall.Wall(pointax, pointay, pointbx, pointby, 200, 100, arcade.color.WHITE, 1))

    def on_key_release(self, key, modifiers):
        self.held_keys.discard(key)

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
                    w.center[0],
                    w.center[1],
                    w.heat*heat_visibility_multiplier,
                    (255, 255, 0, clamp_alpha(int(w.heat * (heat_visibility_multiplier/3))))
                )
            if w.detected:
                w.color = arcade.color.GREEN
            else:
                w.color = arcade.color.WHITE
            for i in w.midpoints:
                arcade.draw_circle_filled(i[0], i[1], 4, arcade.color.RED)
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
            arcade.draw_circle_filled(w.x1, w.y1, 5, arcade.color.AFRICAN_VIOLET)
            arcade.draw_circle_filled(w.x2, w.y2, 5, arcade.color.AIR_FORCE_BLUE)

        for proj in self.projectiles:
            if proj.heat > 0:
                arcade.draw_circle_filled(
                    proj.x,
                    proj.y,
                    proj.heat*heat_visibility_multiplier,
                    (255, 255, 0, clamp_alpha(int(proj.heat * (heat_visibility_multiplier/3))))
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
                        (proj.color[0], proj.color[1], proj.color[2], clamp_alpha(proj.heat * heat_visibility_multiplier)),
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
                (proj.color[0], proj.color[1], proj.color[2], clamp_alpha(proj.color[3]))
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
        self.projectile_spawner(arcade.key.B, delta_time, color=arcade.color.RED, projectile_type="bullet", heat=50, automatic=False)
        self.projectile_spawner(arcade.key.O, delta_time, color=arcade.color.ORANGE, projectile_type="rocket", thrust=45, heat=120)
        self.projectile_spawner(arcade.key.H, delta_time, color=arcade.color.PURPLE, turn_rate=10, projectile_type="heat_seeking_missile", heat=120, detection_cone_angle=360, detection_range=300, thrust=40)
        self.projectile_spawner(arcade.key.F, delta_time, color=arcade.color.YELLOW, projectile_type="flare", heat=255)
        self.projectile_spawner(arcade.MOUSE_BUTTON_LEFT, delta_time, color=arcade.color.RED, projectile_type="bullet", heat=50)
        self.projectile_spawner(arcade.MOUSE_BUTTON_RIGHT, delta_time, color=arcade.color.ORANGE, projectile_type="rocket", thrust=10, heat=100)

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
                # print("ammo destroyed")
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
            if proj.lazy:
                continue
            drag = air_density * np.sqrt(proj.vx**2 + proj.vy**2)
            proj.vy -= gravity * delta_time
            proj.vx -= drag * proj.vx * delta_time
            proj.vy -= drag * proj.vy * delta_time
            proj.targeting(self.walls, self.projectiles, delta_time)
            for w in self.walls:
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
                            if proj.side == -1:
                                distance_to_midpoint = []
                                for i in w.midpoints:
                                    distance_to_midpoint.append(np.sqrt((proj.x-i[0])**2 + (proj.y-i[1])**2))
                                shortest_distance = distance_to_midpoint.index(min(distance_to_midpoint))
                                proj.side = shortest_distance
                                if shortest_distance == 0 or shortest_distance == 2:
                                    proj.vy = -proj.vy + np.random.randint(-w.Ricochet_Loss_Variation,w.Ricochet_Loss_Variation) - w.Ricochet_Loss
                                elif shortest_distance == 1 or shortest_distance == 3:
                                    proj.vx = -proj.vx + np.random.randint(-w.Ricochet_Loss_Variation,w.Ricochet_Loss_Variation) - w.Ricochet_Loss
                        else:
                            proj.alive = False
                    if mx < w.strength:
                        proj.alive = False
                        break
                    break

game = Game()
arcade.run()