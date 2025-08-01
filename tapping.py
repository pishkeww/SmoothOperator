#tapping


import pygame
import time
import csv
import os
import matplotlib.pyplot as plt

# === Settings ===
DURATION = 20        # seconds
ENFORCE_ALTERNATE = True  # Require A-B-A-B pattern
BUTTON_A = 0         # A button index
BUTTON_B = 1         # B button index
FPS = 60

def run():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Button Tap Task (A & B)")
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    print("Tap A and B as fast as you can!")

    tap_times = []
    tap_buttons = []
    last_button = None
    button_state = [0] * joystick.get_numbuttons()

    start_time = time.time()
    running = True

    while running:
        t = time.time() - start_time
        if t > DURATION:
            running = False
            break

        screen.fill((30, 30, 30))

        pygame.event.pump()
        new_state = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # Check for rising edge (button just pressed)
        for btn in [BUTTON_A, BUTTON_B]:
            if new_state[btn] == 1 and button_state[btn] == 0:
                if ENFORCE_ALTERNATE:
                    if last_button is None or last_button != btn:
                        tap_times.append(t)
                        tap_buttons.append(btn)
                        last_button = btn
                else:
                    tap_times.append(t)
                    tap_buttons.append(btn)

        button_state = new_state

        # Draw status
        tap_count = len(tap_times)
        label = font.render(f"Taps: {tap_count}", True, (255, 255, 255))
        time_left = font.render(f"Time: {int(DURATION - t)}s", True, (200, 200, 200))
        screen.blit(label, (30, 30))
        screen.blit(time_left, (30, 70))

        pygame.draw.rect(screen, (0, 180, 0) if joystick.get_button(BUTTON_A) else (80, 80, 80), (100, 150, 100, 100))
        pygame.draw.rect(screen, (180, 0, 0) if joystick.get_button(BUTTON_B) else (80, 80, 80), (250, 150, 100, 100))
        screen.blit(font.render("A", True, (0, 0, 0)), (140, 190))
        screen.blit(font.render("B", True, (0, 0, 0)), (290, 190))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    # === Analysis ===
    tap_intervals = [t2 - t1 for t1, t2 in zip(tap_times[:-1], tap_times[1:])]
    freq = len(tap_times) / DURATION
    iti_std = round((sum((x - sum(tap_intervals)/len(tap_intervals))**2 for x in tap_intervals) / len(tap_intervals))**0.5, 4) if tap_intervals else 0

    # === Plot ===
    plt.figure(figsize=(8, 4))
    plt.eventplot(tap_times, colors='red', lineoffsets=0.5, linelengths=0.8)
    plt.title("Button Taps Over Time")
    plt.xlabel("Time (s)")
    plt.yticks([])
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # === Summary ===
    print("\n===== Button Tap Summary =====")
    print(f"Taps recorded         : {len(tap_times)}")
    print(f"Tapping frequency     : {freq:.2f} taps/sec")
    print(f"ITI standard deviation: {iti_std:.4f}")
    print(f"Alternation enforced  : {ENFORCE_ALTERNATE}")

    # === Save Option ===
    choice = input("Do you want to save the result? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        ts = int(time.time())
        data_file = f"results/button_tap_{ts}.csv"
        with open(data_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time (s)", "Button"])
            for t, b in zip(tap_times, tap_buttons):
                writer.writerow([t, 'A' if b == BUTTON_A else 'B'])
        print(f"[✔] Data saved to {data_file}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run()
