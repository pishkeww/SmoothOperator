import pygame
import time
import math
import csv
import os
import random
import matplotlib.pyplot as plt

# === settings ===
WIDTH, HEIGHT = 800, 600
CURSOR_RADIUS = 5
TARGET_WIDTHS = [40, 60, 80]   
DISTANCES = [200, 300, 400]    # pdistance in pixel
NUM_TRIALS = 9
FPS = 60
DEADZONE = 0.1
SCALE_CURVE = 0.5
TRACK_RADIUS = 250
BUFFER_TIME = 5  # seconds

def scale_input(val, curve=0.5):
    return math.copysign(abs(val) ** curve, val)

def run():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fitts' Law Task")
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    center_y = HEIGHT // 2
    center_x = WIDTH // 2

    # === Buffer Phase ===
    print("Starting buffer phase...")
    buffer_start = time.time()
    while time.time() - buffer_start < BUFFER_TIME:
        screen.fill((25, 25, 25))
        pygame.event.pump()
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        x = 0 if abs(x) < DEADZONE else scale_input(x, SCALE_CURVE)
        y = 0 if abs(y) < DEADZONE else scale_input(y, SCALE_CURVE)

        cursor_x = int(center_x + x * TRACK_RADIUS)
        cursor_y = int(center_y + y * TRACK_RADIUS)
        pygame.draw.circle(screen, (0, 255, 0), (cursor_x, cursor_y), CURSOR_RADIUS)

        text = font.render("Get Ready...", True, (255, 255, 0))
        screen.blit(text, (WIDTH // 2 - 100, 50))
        pygame.display.flip()
        clock.tick(FPS)

    print("Starting trials...")

    trials = []
    direction = 1  # start moving right

    for trial_num in range(NUM_TRIALS):
        # randomize target
        W = random.choice(TARGET_WIDTHS)
        D = random.choice(DISTANCES)

        start_x = center_x - (D // 2) * direction
        end_x = center_x + (D // 2) * direction
        target_rect = pygame.Rect(end_x - W // 2, center_y - W // 2, W, W)

        # Wait at start position
        while True:
            screen.fill((30, 30, 30))
            pygame.draw.rect(screen, (100, 100, 255), target_rect)
            pygame.draw.circle(screen, (255, 255, 255), (start_x, center_y), 8)

            pygame.event.pump()
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            x = 0 if abs(x) < DEADZONE else scale_input(x, SCALE_CURVE)
            y = 0 if abs(y) < DEADZONE else scale_input(y, SCALE_CURVE)

            cursor_x = int(center_x + x * TRACK_RADIUS)
            cursor_y = int(center_y + y * TRACK_RADIUS)
            pygame.draw.circle(screen, (0, 255, 0), (cursor_x, cursor_y), CURSOR_RADIUS)

            text = font.render(f"Trial {trial_num + 1}/{NUM_TRIALS}", True, (220, 220, 220))
            screen.blit(text, (20, 20))
            pygame.display.flip()
            clock.tick(FPS)

            if math.hypot(cursor_x - start_x, cursor_y - center_y) < W:
                break

        # Start 
        path = []
        t0 = time.time()
        hit = False
        while True:
            screen.fill((20, 20, 20))
            pygame.draw.rect(screen, (255, 100, 100), target_rect)

            pygame.event.pump()
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            x = 0 if abs(x) < DEADZONE else scale_input(x, SCALE_CURVE)
            y = 0 if abs(y) < DEADZONE else scale_input(y, SCALE_CURVE)

            cursor_x = int(center_x + x * TRACK_RADIUS)
            cursor_y = int(center_y + y * TRACK_RADIUS)
            pygame.draw.circle(screen, (0, 255, 0), (cursor_x, cursor_y), CURSOR_RADIUS)

            pygame.display.flip()
            clock.tick(FPS)

            path.append((time.time() - t0, cursor_x, cursor_y))

            if target_rect.collidepoint(cursor_x, cursor_y):
                hit = True
                break
            if time.time() - t0 > 3:
                break

        t1 = time.time()
        MT = t1 - t0
        ID = math.log2(D / W + 1)
        IP = ID / MT if MT > 0 else 0
        accuracy = int(hit)

        trials.append({
            "Trial": trial_num + 1,
            "Distance": D,
            "Width": W,
            "MT": round(MT, 3),
            "ID": round(ID, 3),
            "IP": round(IP, 3),
            "Hit": accuracy,
            "Path": path
        })

        direction *= -1

    pygame.quit()

    # === Plot Results ===
    ids = [t["ID"] for t in trials]
    mts = [t["MT"] for t in trials]

    plt.figure(figsize=(6, 4))
    plt.scatter(ids, mts, color='teal')
    plt.title("Fitts' Law: Movement Time vs Index of Difficulty")
    plt.xlabel("Index of Difficulty (ID)")
    plt.ylabel("Movement Time (s)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # === Save Results ===
    choice = input("Do you want to save the results? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        filename = os.path.join("results", f"fitts_law_{int(time.time())}.csv")
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "Distance", "Width", "MT", "ID", "IP", "Hit"])
            for t in trials:
                writer.writerow([t["Trial"], t["Distance"], t["Width"], t["MT"], t["ID"], t["IP"], t["Hit"]])
        print(f"[✔] Results saved to {filename}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run()
