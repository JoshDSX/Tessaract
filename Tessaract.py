import pygame
import numpy as np
import math
import ctypes as ct

# Hide the console window
ct.windll.user32.ShowWindow(ct.windll.kernel32.GetConsoleWindow(), 0)

# --- Configuration ---
WINDOW_SIZE = 800
WINDOW_CENTER = WINDOW_SIZE / 2
PROJECTION_DISTANCE = 5
SCALE = 150
ROTATION_SPEED = 0.01

# --- Colors ---
BACKGROUND_COLOR = (10, 10, 40)
LINE_COLOR = (200, 220, 255)
LINE_WIDTH = 2

def main():
    """Main function to set up and run the simulation."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("4D Tesseract Rotation")
    clock = pygame.time.Clock()

    # Define the 16 vertices of a tesseract in 4D
    # Each coordinate is either -1 or 1
    points_4d = np.array([
        [x, y, z, w]
        for x in [-1, 1]
        for y in [-1, 1]
        for z in [-1, 1]
        for w in [-1, 1]
    ])

    # Define the 32 edges connecting the vertices
    edges = []
    for i in range(16):
        for j in range(i + 1, 16):
            # Two vertices are connected if they differ by exactly one coordinate
            if np.sum(np.abs(points_4d[i] - points_4d[j])) == 2:
                edges.append((i, j))

    angle_xy = 0
    angle_zw = 0
    angle_xw = 0
    angle_yz = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- 4D Rotation ---
        # We rotate around 2D planes in 4D space. Let's use two for a complex motion.
        
        # Rotation in the ZW plane
        rotation_zw = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, math.cos(angle_zw), -math.sin(angle_zw)],
            [0, 0, math.sin(angle_zw), math.cos(angle_zw)]
        ])

        # Rotation in the XW plane
        rotation_xw = np.array([
            [math.cos(angle_xw), 0, 0, -math.sin(angle_xw)],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [math.sin(angle_xw), 0, 0, math.cos(angle_xw)]
        ])
        
        # Combine rotations and apply to all points
        rotated_points = points_4d @ rotation_zw @ rotation_xw

        # --- Projection from 4D to 3D, then 3D to 2D ---
        projected_points_2d = []
        for point in rotated_points:
            x, y, z, w = point

            # Perspective projection from 4D to 3D
            # The 'w' value acts as a depth.
            perspective_w = PROJECTION_DISTANCE / (PROJECTION_DISTANCE - w)
            point_3d = np.array([x, y, z]) * perspective_w

            # Perspective projection from 3D to 2D
            # The 'z' value now acts as depth.
            perspective_z = PROJECTION_DISTANCE / (PROJECTION_DISTANCE - point_3d[2])
            x_2d = point_3d[0] * perspective_z * SCALE + WINDOW_CENTER
            y_2d = point_3d[1] * perspective_z * SCALE + WINDOW_CENTER
            
            projected_points_2d.append((x_2d, y_2d))

        # --- Drawing ---
        screen.fill(BACKGROUND_COLOR)
        for edge in edges:
            start_point = projected_points_2d[edge[0]]
            end_point = projected_points_2d[edge[1]]
            pygame.draw.line(screen, LINE_COLOR, start_point, end_point, LINE_WIDTH)

        pygame.display.flip()

        # Update angles for the next frame
        angle_zw += ROTATION_SPEED
        angle_xw += ROTATION_SPEED / 2 # Rotate at a different speed for more complexity
        
        clock.tick(60) # Limit to 60 frames per second

    pygame.quit()

if __name__ == "__main__":
    main()
