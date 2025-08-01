import pygame
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.fft import fft, fftfreq

# ========== Settings ==========
BUFFER_TIME = 5       # buffer time
DURATION = 20         # test duration in sec
DEADZONE = 0.05
FPS = 60              # frame rate
RADIUS = 150          # radius 



pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick detected.")
joystick = pygame.joystick.Joystick(0)
joystick.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Joystick Circle Tracking")
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()


center_x, center_y = WIDTH // 2, HEIGHT // 2

# ===== BUFFER PHASE =====
print("Hold the joystick cursor steady on the circle...")
buffer_start = time.time()
while time.time() - buffer_start < BUFFER_TIME:
    screen.fill((20, 20, 20))
    pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), RADIUS, 2)
    text = font.render("Get Ready: Keep the dot on the circle...", True, (255, 255, 0))
    screen.blit(text, (20, 20))

    pygame.event.pump()
    x = joystick.get_axis(0)
    y = joystick.get_axis(1)
    x = 0 if abs(x) < DEADZONE else x
    y = 0 if abs(y) < DEADZONE else y
    screen_x = int(center_x + x * RADIUS)
    screen_y = int(center_y + y * RADIUS)
    pygame.draw.circle(screen, (0, 255, 255), (screen_x, screen_y), 6)

    pygame.display.flip()
    clock.tick(FPS)

# ===== TEST PHASE =====
print("Tracking started.")
data = []
start_time = time.time()
running = True

while running:
    screen.fill((30, 30, 30))
    pygame.draw.circle(screen, (100, 100, 100), (center_x, center_y), RADIUS, 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read joystick values
    x = joystick.get_axis(0)
    y = joystick.get_axis(1)
    x = 0 if abs(x) < DEADZONE else x
    y = 0 if abs(y) < DEADZONE else y

    #  dot
    screen_x = int(center_x + x * RADIUS)
    screen_y = int(center_y + y * RADIUS)
    pygame.draw.circle(screen, (0, 255, 0), (screen_x, screen_y), 6)

   
    t = time.time() - start_time
    data.append((t, x, y))

    # Display timer
    remaining = DURATION - t
    timer_text = font.render(f"Time left: {int(remaining)}s", True, (220, 220, 220))
    screen.blit(timer_text, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

    if t >= DURATION:
        running = False

pygame.quit()

# ===== ANALYSIS =====
times = [t for t, _, _ in data]
xs = [x for _, x, _ in data]
ys = [y for _, _, y in data]

# Path radius at each point
radii = [np.sqrt(x**2 + y**2) for x, y in zip(xs, ys)]
radius_errors = [abs(1.0 - r) for r in radii]

# Tremor analysis (FFT)
fs = FPS
n = len(xs)
frequencies = fftfreq(n, 1/fs)
x_fft = fft(xs)
magnitudes = np.abs(x_fft[:n//2])
freqs = frequencies[:n//2]
tremor_band = (freqs >= 4) & (freqs <= 6)
tremor_peak = np.max(magnitudes[tremor_band]) if np.any(tremor_band) else 0

# Jerk (movement roughness)
dx = np.diff(xs)
dy = np.diff(ys)
speed = np.sqrt(dx**2 + dy**2)
jerk = np.abs(np.diff(speed))
mean_jerk = np.mean(jerk)

# Scores
mean_error = np.mean(radius_errors)
max_error = np.max(radius_errors)
score = max(0, 100 - (mean_error * 50 + tremor_peak * 20 + mean_jerk * 10))

# ===== PLOTS =====
plt.figure(figsize=(6, 6))
plt.plot(xs, ys, label="Joystick Path", color='lime')
circle = plt.Circle((0, 0), 1.0, color='gray', linestyle='--', fill=False, label='Ideal Circle')
plt.gca().add_patch(circle)
plt.title("Joystick Movement Path")
plt.xlabel("X")
plt.ylabel("Y")
plt.gca().set_aspect('equal')
plt.gca().invert_yaxis()
plt.legend()
plt.grid(True)

plt.figure()
plt.plot(times, radii)
plt.title("Distance from Center Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Radius")
plt.grid(True)

plt.figure()
plt.plot(freqs, magnitudes)
plt.title("Frequency Spectrum (X-Axis)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)

plt.show()

# ===== REPORT =====
print("\n===== Joystick Tracking Summary =====")
print(f"Mean Path Error     : {mean_error:.4f}")
print(f"Max Path Error      : {max_error:.4f}")
print(f"Tremor Peak (4–6Hz) : {tremor_peak:.2f}")
print(f"Mean Jerkiness      : {mean_jerk:.4f}")
print(f"Control Score (0–100): {score:.1f}")
