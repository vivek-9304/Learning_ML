import pygame
import random
import math
import sys

# ----------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hill Climb Racing - Pygame Edition")
clock = pygame.time.Clock()
FPS = 60

font_small = pygame.font.Font(None, 24)
font_hud = pygame.font.Font(None, 30)
font_medium = pygame.font.Font(None, 44)
font_large = pygame.font.Font(None, 88)

# ----------------------------------------------------------------------
# COLORS
# ----------------------------------------------------------------------
SKY_TOP = (96, 172, 230)
SKY_BOTTOM = (214, 236, 255)
BG_HILL_COLOR = (150, 200, 150)
GROUND_COLOR = (128, 84, 48)
GRASS_COLOR = (86, 168, 74)
CAR_BODY_COLOR = (216, 48, 55)
CAR_BODY_OUTLINE = (40, 15, 15)
CAR_WINDOW_COLOR = (176, 226, 255)
WHEEL_COLOR = (25, 25, 28)
WHEEL_RIM_COLOR = (200, 200, 205)
WHEEL_SPOKE_COLOR = (90, 90, 95)
DRIVER_COLOR = (255, 205, 150)
COIN_COLOR = (255, 205, 30)
COIN_SHADOW = (180, 130, 10)
COIN_HILIGHT = (255, 240, 170)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
TEXT_DARK = (35, 30, 25)
FUEL_BG = (60, 55, 50)

# ----------------------------------------------------------------------
# TUNING CONSTANTS
# ----------------------------------------------------------------------
GRAVITY = 0.32
ENGINE_POWER = 0.30
BRAKE_POWER = 0.45
GRAVITY_SLOPE = 0.35
ROLL_FRICTION = 0.995
MAX_FORWARD_SPEED = 13.0
MAX_REVERSE_SPEED = -6.0
ANGLE_SMOOTH = 0.16
CRASH_ANGLE_THRESHOLD = math.radians(78)
AIR_ROTATE_ACCEL = 0.011
MAX_ANGULAR_VEL = 0.22
AIR_DAMP = 0.99

FUEL_MAX = 100.0
FUEL_GAS_COST = 0.035
FUEL_IDLE_COST = 0.008

COIN_VALUE = 50
FLIP_BONUS = 150
PIXELS_PER_METER = 8.0
START_X = 150.0

# Car geometry (local coords, origin = car center, +x right, +y down)
BODY_LOCAL_POINTS = [
    (-40, 14), (-40, -2), (-24, -20), (10, -22), (30, -8), (44, -2), (44, 14)
]
WINDOW_LOCAL_POINTS = [(-20, -4), (-14, -16), (6, -18), (18, -6)]
DRIVER_LOCAL = (-3, -13)
DRIVER_RADIUS = 6
FRONT_LOCAL = (30, 16)
REAR_LOCAL = (-30, 16)
WHEEL_R = 15

# ----------------------------------------------------------------------
# MATH HELPERS
# ----------------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def rotate_point(x, y, angle):
    c, s = math.cos(angle), math.sin(angle)
    return (x * c - y * s, x * s + y * c)


def normalize_angle(a):
    a = math.fmod(a + math.pi, 2 * math.pi)
    if a < 0:
        a += 2 * math.pi
    return a - math.pi


def lerp_angle(a, b, t):
    return a + normalize_angle(b - a) * t


# ----------------------------------------------------------------------
# TERRAIN
# ----------------------------------------------------------------------
def new_terrain_params():
    return {
        'f1': random.uniform(0.004, 0.007), 's1': random.uniform(0, 1000), 'a1': random.uniform(70, 110),
        'f2': random.uniform(0.009, 0.015), 's2': random.uniform(0, 1000), 'a2': random.uniform(25, 45),
        'f3': random.uniform(0.02, 0.03), 's3': random.uniform(0, 1000), 'a3': random.uniform(4, 10),
        'bf1': random.uniform(0.0006, 0.001), 'bs1': random.uniform(0, 1000), 'ba1': random.uniform(60, 100),
        'bf2': random.uniform(0.0012, 0.002), 'bs2': random.uniform(0, 1000), 'ba2': random.uniform(20, 40),
    }


def terrain_height(x, p):
    base = HEIGHT * 0.68
    ramp = clamp((x - 250) / 450.0, 0.0, 1.0)
    h = (math.sin(x * p['f1'] + p['s1']) * p['a1'] +
         math.sin(x * p['f2'] + p['s2']) * p['a2'] +
         math.sin(x * p['f3'] + p['s3']) * p['a3'])
    return base - h * ramp


def bg_hill_height(x, p):
    base = HEIGHT * 0.5
    h = (math.sin(x * p['bf1'] + p['bs1']) * p['ba1'] +
         math.sin(x * p['bf2'] + p['bs2']) * p['ba2'])
    return base - h


# ----------------------------------------------------------------------
# CAR
# ----------------------------------------------------------------------
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.speed = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.angular_vel = 0.0
        self.grounded = True
        self.air_start_angle = 0.0
        self.wheel_spin = 0.0
        self.fuel = FUEL_MAX
        self.coins = 0
        self.flips = 0
        self.bonus_score = 0
        self.distance = 0.0
        self.crashed = False
        self.out_of_fuel = False
        self.crash_reason = ""
        self.crash_particles_spawned = False

    def wheel_world(self, local):
        rx, ry = rotate_point(local[0], local[1], self.angle)
        return (self.x + rx, self.y + ry)

    def ground_reference(self, params):
        front_w = self.wheel_world(FRONT_LOCAL)
        rear_w = self.wheel_world(REAR_LOCAL)
        front_gy = terrain_height(front_w[0], params) - WHEEL_R
        rear_gy = terrain_height(rear_w[0], params) - WHEEL_R
        slope = math.atan2(front_gy - rear_gy, front_w[0] - rear_w[0])
        fr = rotate_point(FRONT_LOCAL[0], FRONT_LOCAL[1], self.angle)
        rr = rotate_point(REAR_LOCAL[0], REAR_LOCAL[1], self.angle)
        mid_local_y = (fr[1] + rr[1]) / 2.0
        mid_ground_y = (front_gy + rear_gy) / 2.0
        target_y = mid_ground_y - mid_local_y
        return slope, target_y

    def total_score(self):
        return int(self.distance) + self.bonus_score

    def update(self, keys, params):
        """Advance physics by one frame. Returns a popup tuple or None."""
        if self.crashed or self.out_of_fuel:
            return None

        gas = keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_w]
        brake = keys[pygame.K_LEFT] or keys[pygame.K_DOWN] or keys[pygame.K_s]
        popup = None

        if self.grounded:
            slope, _ = self.ground_reference(params)
            self.angle = lerp_angle(self.angle, slope, ANGLE_SMOOTH)

            accel = 0.0
            if gas:
                accel += ENGINE_POWER
            if brake:
                accel -= BRAKE_POWER
            accel += GRAVITY_SLOPE * math.sin(slope)

            self.speed += accel
            self.speed *= ROLL_FRICTION
            self.speed = clamp(self.speed, MAX_REVERSE_SPEED, MAX_FORWARD_SPEED)

            self.x += self.speed * math.cos(self.angle)
            self.x = max(self.x, 20.0)
            self.wheel_spin += self.speed * 0.09

            slope2, target_y2 = self.ground_reference(params)
            self.angle = lerp_angle(self.angle, slope2, ANGLE_SMOOTH)

            self.vy += GRAVITY
            self.y += self.vy

            if self.y >= target_y2:
                self.y = target_y2
                self.vy = 0.0
                self.grounded = True
                diff = normalize_angle(self.angle - slope2)
                if abs(diff) > CRASH_ANGLE_THRESHOLD:
                    self.crashed = True
                    self.crash_reason = "YOUR CAR FLIPPED OVER!"
            else:
                self.grounded = False
                self.vx = self.speed * math.cos(self.angle)
                self.vy = self.speed * math.sin(self.angle) * 0.4 - 1.6
                self.air_start_angle = self.angle
                self.angular_vel = 0.0

            self.fuel -= FUEL_GAS_COST if gas else FUEL_IDLE_COST

        else:
            if gas:
                self.angular_vel += AIR_ROTATE_ACCEL
            if brake:
                self.angular_vel -= AIR_ROTATE_ACCEL
            self.angular_vel = clamp(self.angular_vel, -MAX_ANGULAR_VEL, MAX_ANGULAR_VEL)
            self.angle += self.angular_vel
            self.angular_vel *= AIR_DAMP

            self.vy += GRAVITY
            self.x += self.vx
            self.x = max(self.x, 20.0)
            self.y += self.vy
            self.wheel_spin += self.vx * 0.09

            total_rot = self.angle - self.air_start_angle
            if total_rot >= 2 * math.pi:
                self.flips += 1
                self.bonus_score += FLIP_BONUS
                self.air_start_angle += 2 * math.pi
                popup = ("FLIP! +{}".format(FLIP_BONUS), COIN_COLOR)
            elif total_rot <= -2 * math.pi:
                self.flips += 1
                self.bonus_score += FLIP_BONUS
                self.air_start_angle -= 2 * math.pi
                popup = ("FLIP! +{}".format(FLIP_BONUS), COIN_COLOR)

            slope2, target_y2 = self.ground_reference(params)
            if self.y >= target_y2:
                self.y = target_y2
                self.angle = slope2 + normalize_angle(self.angle - slope2)
                diff = normalize_angle(self.angle - slope2)
                if abs(diff) > CRASH_ANGLE_THRESHOLD:
                    self.crashed = True
                    self.crash_reason = "CRASHED ON LANDING!"
                self.speed = self.vx
                self.vy = 0.0
                self.grounded = True

            self.fuel -= FUEL_IDLE_COST

        self.fuel = clamp(self.fuel, 0.0, FUEL_MAX)
        if self.fuel <= 0 and not self.crashed:
            self.out_of_fuel = True

        self.distance = max(self.distance, (self.x - START_X) / PIXELS_PER_METER)
        return popup


# ----------------------------------------------------------------------
# DRAWING HELPERS
# ----------------------------------------------------------------------
def make_sky_surface():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for yy in range(HEIGHT):
        t = yy / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, yy), (WIDTH, yy))
    return surf


SKY_SURFACE = make_sky_surface()


def draw_sun(surface, cam_x, cam_y):
    sx = WIDTH - 130 - (cam_x * 0.05) % 40
    sy = 90 + (cam_y * 0.05)
    pygame.draw.circle(surface, (255, 240, 180), (int(sx), int(sy)), 46)
    pygame.draw.circle(surface, (255, 250, 210), (int(sx), int(sy)), 46, 4)


def draw_cloud(surface, sx, sy, scale=1.0):
    pygame.draw.ellipse(surface, WHITE, (sx - 30 * scale, sy - 12 * scale, 60 * scale, 26 * scale))
    pygame.draw.circle(surface, WHITE, (int(sx - 16 * scale), int(sy)), int(15 * scale))
    pygame.draw.circle(surface, WHITE, (int(sx + 10 * scale), int(sy - 8 * scale)), int(17 * scale))
    pygame.draw.circle(surface, WHITE, (int(sx + 26 * scale), int(sy)), int(12 * scale))


def draw_background_hills(surface, cam_x, cam_y, params):
    par = 0.4
    points = []
    for sx in range(-60, WIDTH + 70, 30):
        wx = cam_x * par + sx
        wy = bg_hill_height(wx, params) - cam_y * 0.5
        points.append((sx, wy))
    poly = [(-60, HEIGHT + 20)] + points + [(WIDTH + 70, HEIGHT + 20)]
    pygame.draw.polygon(surface, BG_HILL_COLOR, poly)


def draw_terrain(surface, cam_x, cam_y, params):
    points = []
    for sx in range(-40, WIDTH + 50, 10):
        wx = cam_x + sx
        wy = terrain_height(wx, params) - cam_y
        points.append((sx, wy))
    poly = [(-40, HEIGHT + 40)] + points + [(WIDTH + 50, HEIGHT + 40)]
    pygame.draw.polygon(surface, GROUND_COLOR, poly)
    if len(points) >= 2:
        pygame.draw.lines(surface, GRASS_COLOR, False, points, 9)


def draw_coin(surface, sx, sy):
    pygame.draw.circle(surface, COIN_SHADOW, (int(sx), int(sy)), 14)
    pygame.draw.circle(surface, COIN_COLOR, (int(sx), int(sy)), 12)
    pygame.draw.circle(surface, COIN_HILIGHT, (int(sx - 3), int(sy - 3)), 4)


def to_screen(local, car, cam_x, cam_y):
    rx, ry = rotate_point(local[0], local[1], car.angle)
    return (car.x + rx - cam_x, car.y + ry - cam_y)


def draw_car(surface, car, cam_x, cam_y):
    # wheels (drawn first, behind body)
    for local in (REAR_LOCAL, FRONT_LOCAL):
        wx, wy = to_screen(local, car, cam_x, cam_y)
        pygame.draw.circle(surface, WHEEL_COLOR, (int(wx), int(wy)), WHEEL_R)
        pygame.draw.circle(surface, WHEEL_RIM_COLOR, (int(wx), int(wy)), 6)
        spin = car.wheel_spin + car.angle
        ex = wx + math.cos(spin) * (WHEEL_R - 3)
        ey = wy + math.sin(spin) * (WHEEL_R - 3)
        pygame.draw.line(surface, WHEEL_SPOKE_COLOR, (wx, wy), (ex, ey), 3)

    # body
    body_pts = [to_screen(p, car, cam_x, cam_y) for p in BODY_LOCAL_POINTS]
    pygame.draw.polygon(surface, CAR_BODY_COLOR, body_pts)
    pygame.draw.polygon(surface, CAR_BODY_OUTLINE, body_pts, 3)

    # window
    win_pts = [to_screen(p, car, cam_x, cam_y) for p in WINDOW_LOCAL_POINTS]
    pygame.draw.polygon(surface, CAR_WINDOW_COLOR, win_pts)
    pygame.draw.polygon(surface, CAR_BODY_OUTLINE, win_pts, 2)

    # driver
    dx, dy = to_screen(DRIVER_LOCAL, car, cam_x, cam_y)
    pygame.draw.circle(surface, DRIVER_COLOR, (int(dx), int(dy)), DRIVER_RADIUS)


def spawn_crash_particles(particles, x, y):
    palette = [CAR_BODY_COLOR, (90, 90, 90), (130, 130, 130), (255, 190, 70)]
    for _ in range(24):
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(2, 7)
        particles.append({
            'x': x, 'y': y,
            'vx': math.cos(ang) * spd, 'vy': math.sin(ang) * spd - 3,
            'life': 40, 'maxlife': 40,
            'color': random.choice(palette), 'r': random.randint(3, 7),
        })


def update_particles(particles):
    for p in particles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.25
        p['life'] -= 1
    particles[:] = [p for p in particles if p['life'] > 0]


def draw_particles(surface, particles, cam_x, cam_y):
    for p in particles:
        ratio = p['life'] / p['maxlife']
        radius = max(1, int(p['r'] * ratio))
        pygame.draw.circle(surface, p['color'], (int(p['x'] - cam_x), int(p['y'] - cam_y)), radius)


def update_popups(popups):
    for p in popups:
        p['y'] -= 1.0
        p['life'] -= 1
    popups[:] = [p for p in popups if p['life'] > 0]


def draw_popups(surface, popups):
    for p in popups:
        surf = font_medium.render(p['text'], True, p['color'])
        surf.set_alpha(int(255 * clamp(p['life'] / p['maxlife'], 0, 1)))
        surface.blit(surf, (p['x'] - surf.get_width() // 2, p['y']))


def fuel_color(frac):
    if frac > 0.5:
        return (70, 190, 90)
    elif frac > 0.2:
        return (235, 175, 40)
    else:
        return (215, 60, 55)


def draw_hud(surface, car):
    # fuel bar
    bar_x, bar_y, bar_w, bar_h = 20, 20, 220, 22
    pygame.draw.rect(surface, FUEL_BG, (bar_x - 3, bar_y - 3, bar_w + 6, bar_h + 6), border_radius=8)
    frac = car.fuel / FUEL_MAX
    pygame.draw.rect(surface, fuel_color(frac), (bar_x, bar_y, int(bar_w * frac), bar_h), border_radius=6)
    pygame.draw.rect(surface, BLACK, (bar_x - 3, bar_y - 3, bar_w + 6, bar_h + 6), 2, border_radius=8)
    label = font_small.render("FUEL", True, WHITE)
    surface.blit(label, (bar_x + 6, bar_y + 2))

    # coins
    draw_coin(surface, 40, 78)
    coin_text = font_hud.render("x {}".format(car.coins), True, TEXT_DARK)
    surface.blit(coin_text, (58, 66))

    # flips
    flip_text = font_hud.render("Flips: {}".format(car.flips), True, TEXT_DARK)
    surface.blit(flip_text, (20, 100))

    # distance / score top-right
    dist_text = font_hud.render("{} m".format(int(car.distance)), True, TEXT_DARK)
    surface.blit(dist_text, (WIDTH - dist_text.get_width() - 20, 20))
    score_text = font_hud.render("Score: {}".format(car.total_score()), True, TEXT_DARK)
    surface.blit(score_text, (WIDTH - score_text.get_width() - 20, 50))

    # controls hint
    hint = font_small.render("-> / W  Gas      <- / S  Brake", True, TEXT_DARK)
    hint_surf = pygame.Surface((hint.get_width() + 20, hint.get_height() + 10), pygame.SRCALPHA)
    hint_surf.fill((255, 255, 255, 130))
    hint_surf.blit(hint, (10, 5))
    surface.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 40))


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    MENU, PLAYING, GAMEOVER = "menu", "playing", "gameover"
    state = MENU

    menu_params = new_terrain_params()
    menu_cam_x, menu_cam_y = 0.0, 0.0
    menu_clouds = [(random.uniform(0, 2000), random.uniform(60, 200), random.uniform(0.7, 1.3)) for _ in range(6)]

    car = None
    params = None
    coins = []
    clouds = []
    particles = []
    popups = []
    next_coin_x = 0.0
    next_cloud_x = 0.0
    camera_x, camera_y = 0.0, 0.0
    shake_timer = 0
    shake_mag = 0.0

    def reset_game():
        nonlocal car, params, coins, clouds, particles, popups
        nonlocal next_coin_x, next_cloud_x, camera_x, camera_y, shake_timer, shake_mag
        params = new_terrain_params()
        start_y = terrain_height(START_X, params) - WHEEL_R - 16
        car = Car(START_X, start_y)
        coins = []
        clouds = [(random.uniform(0, 1600), random.uniform(60, 200), random.uniform(0.7, 1.3)) for _ in range(6)]
        particles = []
        popups = []
        next_coin_x = START_X + 300
        next_cloud_x = 1600
        camera_x, camera_y = car.x - WIDTH * 0.32, car.y - HEIGHT * 0.58
        shake_timer, shake_mag = 0, 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if state == MENU and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    reset_game()
                    state = PLAYING
                if state == GAMEOVER and event.key == pygame.K_r:
                    reset_game()
                    state = PLAYING

        keys = pygame.key.get_pressed()

        # ---------------- UPDATE ----------------
        if state == MENU:
            menu_cam_x += 1.4
        elif state == PLAYING:
            popup = car.update(keys, params)
            if popup:
                sx, sy = car.x - camera_x, car.y - camera_y - 50
                popups.append({'text': popup[0], 'color': popup[1], 'x': sx, 'y': sy, 'life': 45, 'maxlife': 45})

            # coin generation ahead of camera
            while next_coin_x < camera_x + WIDTH * 1.6:
                gap = random.uniform(200, 360)
                next_coin_x += gap
                cy = terrain_height(next_coin_x, params) - random.uniform(55, 140)
                coins.append({'x': next_coin_x, 'y': cy, 'collected': False, 'phase': random.uniform(0, 6.28)})

            # cloud generation ahead
            while next_cloud_x < camera_x + WIDTH * 2.2:
                next_cloud_x += random.uniform(250, 500)
                clouds.append((next_cloud_x, random.uniform(50, 210), random.uniform(0.7, 1.4)))
            clouds[:] = [c for c in clouds if c[0] > camera_x - 400]

            # coin pickup check
            for coin in coins:
                if coin['collected']:
                    continue
                if abs(coin['x'] - car.x) < 220:
                    dist = math.hypot(coin['x'] - car.x, coin['y'] - car.y)
                    if dist < 34:
                        coin['collected'] = True
                        car.coins += 1
                        car.bonus_score += COIN_VALUE
                        sx, sy = coin['x'] - camera_x, coin['y'] - camera_y - 20
                        popups.append({'text': "+{}".format(COIN_VALUE), 'color': COIN_COLOR,
                                        'x': sx, 'y': sy, 'life': 35, 'maxlife': 35})
            coins[:] = [c for c in coins if not c['collected'] and c['x'] > camera_x - 400]

            update_particles(particles)
            update_popups(popups)

            if car.crashed and not car.crash_particles_spawned:
                spawn_crash_particles(particles, car.x, car.y)
                car.crash_particles_spawned = True
                shake_timer, shake_mag = 18, 10.0

            if car.crashed or car.out_of_fuel:
                state = GAMEOVER
            else:
                target_cx = car.x - WIDTH * 0.32
                target_cy = car.y - HEIGHT * 0.58
                camera_x += (target_cx - camera_x) * 0.12
                camera_y += (target_cy - camera_y) * 0.08

        elif state == GAMEOVER:
            update_particles(particles)

        if shake_timer > 0:
            shake_timer -= 1
            shake_mag *= 0.9
            render_ox = random.uniform(-shake_mag, shake_mag)
            render_oy = random.uniform(-shake_mag, shake_mag)
        else:
            render_ox, render_oy = 0.0, 0.0

        # ---------------- DRAW ----------------
        if state == MENU:
            rcx, rcy = menu_cam_x, menu_cam_y
            screen.blit(SKY_SURFACE, (0, 0))
            draw_sun(screen, rcx, rcy)
            for (cx, cy, sc) in menu_clouds:
                draw_cloud(screen, (cx - rcx * 0.6) % (WIDTH + 200) - 100, cy, sc)
            draw_background_hills(screen, rcx, rcy, menu_params)
            draw_terrain(screen, rcx, rcy, menu_params)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            screen.blit(overlay, (0, 0))

            title = font_large.render("HILL CLIMB", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
            sub = font_medium.render("RACING", True, COIN_COLOR)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 235))

            ctrl1 = font_hud.render("-> or W : Gas        <- or S : Brake", True, WHITE)
            screen.blit(ctrl1, (WIDTH // 2 - ctrl1.get_width() // 2, 340))
            ctrl2 = font_small.render("Tilt in mid-air with Gas/Brake to land flips!", True, WHITE)
            screen.blit(ctrl2, (WIDTH // 2 - ctrl2.get_width() // 2, 375))

            if (pygame.time.get_ticks() // 500) % 2 == 0:
                start_txt = font_medium.render("PRESS SPACE TO START", True, WHITE)
                screen.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 450))

        elif state == PLAYING:
            rcx, rcy = camera_x + render_ox, camera_y + render_oy
            screen.blit(SKY_SURFACE, (0, 0))
            draw_sun(screen, rcx, rcy)
            for (cx, cy, sc) in clouds:
                draw_cloud(screen, cx - rcx * 0.6, cy, sc)
            draw_background_hills(screen, rcx, rcy, params)
            draw_terrain(screen, rcx, rcy, params)

            for coin in coins:
                bob = math.sin(pygame.time.get_ticks() * 0.004 + coin['phase']) * 4
                draw_coin(screen, coin['x'] - rcx, coin['y'] - rcy + bob)

            draw_car(screen, car, rcx, rcy)
            draw_particles(screen, particles, rcx, rcy)
            draw_popups(screen, popups)
            draw_hud(screen, car)

        elif state == GAMEOVER:
            rcx, rcy = camera_x + render_ox, camera_y + render_oy
            screen.blit(SKY_SURFACE, (0, 0))
            draw_sun(screen, rcx, rcy)
            for (cx, cy, sc) in clouds:
                draw_cloud(screen, cx - rcx * 0.6, cy, sc)
            draw_background_hills(screen, rcx, rcy, params)
            draw_terrain(screen, rcx, rcy, params)
            for coin in coins:
                bob = math.sin(pygame.time.get_ticks() * 0.004 + coin['phase']) * 4
                draw_coin(screen, coin['x'] - rcx, coin['y'] - rcy + bob)
            if not car.crashed:
                draw_car(screen, car, rcx, rcy)
            draw_particles(screen, particles, rcx, rcy)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            title = font_large.render("GAME OVER", True, (235, 70, 70))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 90))

            reason = car.crash_reason if car.crashed else "OUT OF FUEL!"
            reason_surf = font_medium.render(reason, True, WHITE)
            screen.blit(reason_surf, (WIDTH // 2 - reason_surf.get_width() // 2, 190))

            stats = [
                "Distance: {} m".format(int(car.distance)),
                "Coins collected: {}".format(car.coins),
                "Flips landed: {}".format(car.flips),
                "TOTAL SCORE: {}".format(car.total_score()),
            ]
            for i, line in enumerate(stats):
                col = COIN_COLOR if i == 3 else WHITE
                s = font_hud.render(line, True, col)
                screen.blit(s, (WIDTH // 2 - s.get_width() // 2, 260 + i * 36))

            if (pygame.time.get_ticks() // 500) % 2 == 0:
                r_txt = font_medium.render("PRESS R TO RESTART", True, WHITE)
                screen.blit(r_txt, (WIDTH // 2 - r_txt.get_width() // 2, 430))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()