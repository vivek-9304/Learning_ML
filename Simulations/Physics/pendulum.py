import pygame
import pymunk
import math

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pymunk Pendulum")

clock = pygame.time.Clock()

# -------------------------
# Pymunk world
# -------------------------

space = pymunk.Space()

# Pygame coordinates: +Y is DOWN
space.gravity = (0, 900)

# -------------------------
# Pivot
# -------------------------

pivot = pymunk.Body(body_type=pymunk.Body.STATIC)
pivot.position = (WIDTH // 2, 250)

pivot_shape = pymunk.Circle(pivot, 10)

space.add(pivot, pivot_shape)

# -------------------------
# Pendulum bob
# -------------------------

mass = 5
radius = 30
length = 250

moment = pymunk.moment_for_circle(
    mass,
    0,
    radius
)

bob = pymunk.Body(mass, moment)

# Start at an angle
theta = math.radians(40)

bob.position = (
    pivot.position.x + length * math.sin(theta),
    pivot.position.y + length * math.cos(theta)
)

bob_shape = pymunk.Circle(bob, radius)

bob_shape.friction = 0.8
bob_shape.elasticity = 0.2

space.add(bob, bob_shape)

# -------------------------
# Pendulum constraint
# -------------------------

joint = pymunk.PinJoint(
    pivot,
    bob
)

space.add(joint)

# -------------------------
# Main loop
# -------------------------

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Physics
    space.step(1 / 60)

    # ---------------------
    # Drawing
    # ---------------------

    screen.fill((20, 20, 30))

    pivot_pos = (
        int(pivot.position.x),
        int(pivot.position.y)
    )

    bob_pos = (
        int(bob.position.x),
        int(bob.position.y)
    )

    # Rod
    pygame.draw.line(
        screen,
        (220, 220, 220),
        pivot_pos,
        bob_pos,
        6
    )

    # Pivot
    pygame.draw.circle(
        screen,
        (255, 80, 80),
        pivot_pos,
        12
    )

    # Bob
    pygame.draw.circle(
        screen,
        (80, 150, 255),
        bob_pos,
        radius
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()