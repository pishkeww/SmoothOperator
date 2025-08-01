import pygame
import numpy as np
import time
import math
import csv
import os
import matplotlib.pyplot as plt

# === settings ===
WIDTH, HEIGHT = 800, 600
DURATION = 20  # seconds
DEADZONE = 0.05
FPS = 60
TRACE_RADIUS = 200

def generate_line(cx, cy):
    return [(cx - 150 + i * 3, cy) for i in range(100)]

def generate_square(cx, cy, size=200):
    x0, y0 = cx - size // 2, cy - size // 2
    square = []
    for i in range(size): square.append((x0 + i, y0))
    for i in range(size): square.append((x0 + size, y0 + i))
    for i in range(size): square.append((x0 + size - i, y0 + size))
    for i in range(size): square.append((x0, y0 + size - i))
    return square

def generate_circle(cx, cy, radius=150):
    theta = np.linspace(0, 2 * np.pi, 300)
    return [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in theta]

def generate_zigzag(cx, cy, width=300, height=100, steps=10):
    path = []
    for i in range(steps):
        x = cx - width // 2 + (i * (width // steps))
        y = cy - height // 2 if i % 2 == 0 else cy + height // 2
        path.append((x, y))
    return path

def select_shape():
    print("Choose shape to trace:")
    print("1. Line")
    print("2. Square")
    print("3. Circle")
    print("4. Zig-Zag")
    choice = input("Enter number [1-4]: ").strip()
    return {
        "1": generate_line,
        "2": generate_square,
        "3": generate_circle,
        "4": generate_zigzag
    }.get(choice, generate_line)

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

    shape_func = select_shape()
    target_path = shape_func(center_x, center_y)

    print("Trace the shape as smoothly and accurately as possible using the joystick.")
    time.sleep(2)

    start_time = time.time()
    data = []
    running = True

    while running:
        t = time.time() - start_time
        if t > DURATION:
            break

        screen.fill((30, 30, 30))
        pygame.draw.lines(screen, (80, 80, 80), False, [(int(x), int(y)) for x, y in target_path], 2)

        pygame.event.pump()
        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        x = 0 if abs(x) < DEADZONE else x
        y = 0 if abs(y) < DEADZONE else y

        cursor_x = center_x + x * TRACE_RADIUS
        cursor_y = center_y + y * TRACE_RADIUS
        pygame.draw.circle(screen, (0, 255, 0), (int(cursor_x), int(cursor_y)), 6)

        data.append([t, x, y])

        timer = font.render(f"Time: {int(DURATION - t)}s", True, (200, 200, 200))
        screen.blit(timer, (20, 20))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    # === Analysis ===
    times = [d[0] for d in data]
    xs = [d[1] * TRACE_RADIUS for d in data]
    ys = [d[2] * TRACE_RADIUS for d in data]

    dx = np.diff(xs)
    dy = np.diff(ys)
    speed = np.sqrt(dx**2 + dy**2)
    jerk = np.abs(np.diff(speed))
    mean_jerk = np.mean(jerk) if len(jerk) > 0 else 0
    speed_std = np.std(speed)

    # Deviation from target path (if same length)
    actual = np.array(list(zip(xs, ys)))
    if len(actual) > len(target_path):
        actual = actual[:len(target_path)]
    target_local = np.array([(x - center_x, y - center_y) for x, y in target_path[:len(actual)]])
    deviation = np.linalg.norm(actual - target_local, axis=1)
    mean_dev = np.mean(deviation)

    # === Plot ===
    plt.figure(figsize=(6, 6))
    plt.plot([x for x, y in target_path], [y for x, y in target_path], '--', label='Target Shape', color='gray')
    plt.plot([center_x + x for x in xs], [center_y + y for y in ys], label='Joystick Path', color='lime')
    plt.title("Path Smoothness Task")
    plt.gca().invert_yaxis()
    plt.gca().set_aspect('equal')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # === Summary ===
    print("\n===== Path Smoothness Summary =====")
    print(f"Mean deviation from shape : {mean_dev:.2f} px")
    print(f"Mean jerkiness             : {mean_jerk:.3f}")
    print(f"Speed variability (std)    : {speed_std:.3f}")
    print(f"Duration                   : {DURATION} sec")

    # === Save Option ===
    choice = input("Do you want to save the result? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        filename = f"results/path_smoothness_{int(time.time())}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Joystick X", "Joystick Y"])
            writer.writerows(data)
        print(f"[✔] Data saved to {filename}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run()
