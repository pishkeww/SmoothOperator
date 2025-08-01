import pygame
import math
import time
import csv
import os
import matplotlib.pyplot as plt

# === Csettings ===
WIDTH, HEIGHT = 800, 600
RADIUS = 150
TRACK_DURATION = 20  # seconds
BUFFER_TIME = 5      # buffer before tracking starts
TARGET_SPEED = 0.2   # rotations per second
DEADZONE = 0.05
FPS = 60

def run():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()
    center_x, center_y = WIDTH // 2, HEIGHT // 2

    # === buffer Phase ===
    buffer_start = time.time()
    while time.time() - buffer_start < BUFFER_TIME:
        t = time.time() - buffer_start
        screen.fill((20, 20, 20))

        angle = 2 * math.pi * TARGET_SPEED * t
        target_x = center_x + RADIUS * math.cos(angle)
        target_y = center_y + RADIUS * math.sin(angle)
        pygame.draw.circle(screen, (255, 100, 100), (int(target_x), int(target_y)), 8)

        pygame.event.pump()
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        x = 0 if abs(x) < DEADZONE else x
        y = 0 if abs(y) < DEADZONE else y
        cursor_x = center_x + x * RADIUS
        cursor_y = center_y + y * RADIUS
        pygame.draw.circle(screen, (0, 255, 0), (int(cursor_x), int(cursor_y)), 6)

        text = font.render("Get Ready: Align with the target...", True, (255, 255, 0))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    # === Tracking Phase ===
    data = []
    start_time = time.time()
    running = True

    while running:
        t = time.time() - start_time
        if t > TRACK_DURATION:
            running = False
            break

        screen.fill((20, 20, 20))

        angle = 2 * math.pi * TARGET_SPEED * (t + BUFFER_TIME)
        target_x = center_x + RADIUS * math.cos(angle)
        target_y = center_y + RADIUS * math.sin(angle)
        pygame.draw.circle(screen, (255, 100, 100), (int(target_x), int(target_y)), 8)

        pygame.event.pump()
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        x = 0 if abs(x) < DEADZONE else x
        y = 0 if abs(y) < DEADZONE else y
        cursor_x = center_x + x * RADIUS
        cursor_y = center_y + y * RADIUS
        pygame.draw.circle(screen, (0, 255, 0), (int(cursor_x), int(cursor_y)), 6)

        error = math.sqrt((target_x - cursor_x) ** 2 + (target_y - cursor_y) ** 2)
        data.append([t, x, y, target_x - center_x, target_y - center_y, error])

        text = font.render(f"Time: {int(TRACK_DURATION - t)}s | Error: {error:.1f}", True, (200, 200, 200))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    # === Plot Results ===
    joystick_x = [x * RADIUS for _, x, _, _, _, _ in data]
    joystick_y = [y * RADIUS for _, _, y, _, _, _ in data]
    target_x = [tx for _, _, _, tx, _, _ in data]
    target_y = [ty for _, _, _, _, ty, _ in data]
    time_axis = [t for t, *_ in data]
    error = [e for *_, e in data]

    # Path plot
    plt.figure(figsize=(6, 6))
    plt.plot(target_x, target_y, label='Target Path', linestyle='--', color='red')
    plt.plot(joystick_x, joystick_y, label='Joystick Path', color='lime')
    plt.title("Target Tracking - Joystick vs. Target Path")
    plt.xlabel("X position")
    plt.ylabel("Y position")
    plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Error over time
    plt.figure(figsize=(8, 4))
    plt.plot(time_axis, error, label='Tracking Error', color='orange')
    plt.title("Error Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Error (pixels)")
    plt.grid(True)
    plt.tight_layout()

    plt.show()

    # ===  Save ===
    choice = input("Do you want to save the result? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        filename = os.path.join("results", f"target_tracking_{int(time.time())}.csv")
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Joystick X", "Joystick Y", "Target X", "Target Y", "Error"])
            writer.writerows(data)
        print(f"[✔] Data saved to {filename}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run()
