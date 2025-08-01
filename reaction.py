import pygame
import time
import math
import csv
import os
import random
import matplotlib.pyplot as plt

# === settings ===
WIDTH, HEIGHT = 800, 600
TARGET_RADIUS = 30
JOYSTICK_RADIUS = 250
DEADZONE = 0.1
NUM_TRIALS = 5
FPS = 60
MIN_DELAY = 2  # just so that stimulus appears after 2–5s
MAX_DELAY = 5

def run():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reaction + Movement Task")
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    center_x, center_y = WIDTH // 2, HEIGHT // 2

    results = []

    for trial in range(NUM_TRIALS):
        # Random target position around a circle
        angle = random.uniform(0, 2 * math.pi)
        target_x = center_x + JOYSTICK_RADIUS * math.cos(angle)
        target_y = center_y + JOYSTICK_RADIUS * math.sin(angle)
        target_pos = (int(target_x), int(target_y))

        # === wait phase Before Stimulus Appears ===
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        pre_stim_time = time.time()
        while time.time() - pre_stim_time < delay:
            screen.fill((20, 20, 20))
            text = font.render(f"Trial {trial+1}/{NUM_TRIALS} — Wait...", True, (200, 200, 200))
            screen.blit(text, (20, 20))
            pygame.display.flip()
            clock.tick(FPS)

        # === Stimulus Appears ===
        stim_time = time.time()
        movement_started = False
        movement_start_time = None
        reached_target = False
        movement_path = []

        while not reached_target:
            screen.fill((30, 30, 30))
            pygame.draw.circle(screen, (255, 100, 100), target_pos, TARGET_RADIUS)
            pygame.event.pump()

            # Read joystick input
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            x = 0 if abs(x) < DEADZONE else x
            y = 0 if abs(y) < DEADZONE else y

            cursor_x = int(center_x + x * JOYSTICK_RADIUS)
            cursor_y = int(center_y + y * JOYSTICK_RADIUS)
            pygame.draw.circle(screen, (0, 255, 0), (cursor_x, cursor_y), 8)

            # Detect movement onset
            if not movement_started and (abs(x) > DEADZONE or abs(y) > DEADZONE):
                movement_started = True
                movement_start_time = time.time()

            # Check if target is reached
            if movement_started and math.hypot(cursor_x - target_x, cursor_y - target_y) < TARGET_RADIUS:
                reached_target = True
                arrival_time = time.time()

            movement_path.append((time.time() - stim_time, x, y))
            pygame.display.flip()
            clock.tick(FPS)

        # === Store Trial Result ===
        srt = movement_start_time - stim_time if movement_start_time else None
        mt = arrival_time - movement_start_time if movement_start_time else None
        total_rt = arrival_time - stim_time

        results.append({
            "trial": trial + 1,
            "srt": round(srt, 4),
            "mt": round(mt, 4),
            "total_rt": round(total_rt, 4),
            "path": movement_path
        })

    pygame.quit()

    # === Plot ===
    path = results[-1]["path"]
    path_x = [x * JOYSTICK_RADIUS for _, x, _ in path]
    path_y = [y * JOYSTICK_RADIUS for _, _, y in path]
    plt.figure(figsize=(6, 6))
    plt.plot(path_x, path_y, color='blue', label='Joystick Path')
    plt.scatter([0], [0], color='gray', label='Start')
    plt.scatter([JOYSTICK_RADIUS * math.cos(angle)], [JOYSTICK_RADIUS * math.sin(angle)],
                color='red', label='Target')
    plt.title("Joystick Path to Target")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # === Print Summary ===
    print("\n===== Reaction + Movement Summary =====")
    for r in results:
        print(f"Trial {r['trial']}: SRT = {r['srt']}s | MT = {r['mt']}s | Total = {r['total_rt']}s")

    # === Save Option ===
    choice = input("Do you want to save the results? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        ts = int(time.time())
        main_file = f"results/reaction_movement_{ts}.csv"
        with open(main_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Trial", "SRT", "MT", "Total_RT"])
            for r in results:
                writer.writerow([r["trial"], r["srt"], r["mt"], r["total_rt"]])
        print(f"[✔] Summary saved to {main_file}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run()
