import pygame
import numpy as np
import math
import time
import random
import csv
import os

# === Settings ===
WIDTH, HEIGHT = 800, 600
DURATION = 30  # seconds
DEADZONE = 0.05
FPS = 60
RADIUS = 150
TARGET_SPEED = 0.2  # rotations per second
QUESTION_INTERVAL = 5  # seconds


BUTTON_MAP = {
    0: 'A',  
    1: 'B',  
    2: 'X',  
    3: 'Y',  
}

def generate_mcq():
    a, b = random.randint(1, 9), random.randint(1, 9)
    correct = a + b
    options = random.sample(range(2, 19), 3)
    if correct not in options:
        options[random.randint(0, 2)] = correct
    options = list(set(options))  # remove duplicates
    while len(options) < 4:
        val = random.randint(2, 18)
        if val not in options:
            options.append(val)
    random.shuffle(options)
    return f"{a} + {b} = ?", correct, options

def run_dual_task_mcq():
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

    print("Dual-task test: Follow the moving target AND answer math questions using A/B/X/Y.")
    time.sleep(2)

    start_time = time.time()
    last_question_time = -QUESTION_INTERVAL
    question, correct_ans, options = "", None, []
    response_start = None

    motor_data = []
    cognitive_data = []
    option_labels = ['A', 'B', 'X', 'Y']

    running = True
    while running:
        t = time.time() - start_time
        if t > DURATION:
            break

        if t - last_question_time >= QUESTION_INTERVAL:
            question, correct_ans, options = generate_mcq()
            last_question_time = t
            response_start = time.time()

        screen.fill((20, 20, 20))

        # Target 
        angle = 2 * math.pi * TARGET_SPEED * t
        tx = center_x + RADIUS * math.cos(angle)
        ty = center_y + RADIUS * math.sin(angle)
        pygame.draw.circle(screen, (255, 100, 100), (int(tx), int(ty)), 8)

        # input
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN and correct_ans:
                btn = event.button
                if btn in BUTTON_MAP:
                    label = BUTTON_MAP[btn]
                    selected_index = option_labels.index(label)
                    selected_val = options[selected_index] if selected_index < len(options) else None
                    correct = selected_val == correct_ans
                    rt = time.time() - response_start
                    cognitive_data.append([question, correct_ans, selected_val, correct, rt])
                    question, correct_ans, options = "", None, []

        x = joystick.get_axis(0)
        y = joystick.get_axis(1)
        x = 0 if abs(x) < DEADZONE else x
        y = 0 if abs(y) < DEADZONE else y

        cx = center_x + x * RADIUS
        cy = center_y + y * RADIUS
        pygame.draw.circle(screen, (0, 255, 0), (int(cx), int(cy)), 6)

        error = math.sqrt((tx - cx) ** 2 + (ty - cy) ** 2)
        motor_data.append([t, x, y, tx - center_x, ty - center_y, error])

        info = font.render(f"Time Left: {int(DURATION - t)}s | Error: {error:.1f}", True, (220, 220, 220))
        screen.blit(info, (20, 20))

        if question:
            screen.blit(font.render(f"{question}", True, (255, 255, 0)), (20, 60))
            for i, opt in enumerate(options[:4]):
                label = option_labels[i]
                screen.blit(font.render(f"{label}: {opt}", True, (180, 180, 180)), (20, 100 + 30 * i))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    # === Results y ===
    errors = [row[-1] for row in motor_data]
    mean_error = np.mean(errors)
    error_std = np.std(errors)
    correct = sum(1 for q in cognitive_data if q[3])
    total = len(cognitive_data)

    print("\n===== Dual-Task Summary =====")
    print(f"Mean tracking error : {mean_error:.2f} px")
    print(f"Tracking error SD   : {error_std:.2f}")
    print(f"Correct answers     : {correct}/{total}")
    if total > 0:
        rt_list = [row[4] for row in cognitive_data]
        print(f"Mean reaction time  : {np.mean(rt_list):.3f} s")

    # === Save Option ===
    choice = input("Save results to CSV? (Y/N): ").strip().lower()
    if choice == 'y':
        os.makedirs("results", exist_ok=True)
        ts = int(time.time())
        motor_file = f"results/dual_motor_mcq_{ts}.csv"
        cog_file = f"results/dual_cognitive_mcq_{ts}.csv"

        with open(motor_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Joystick X", "Joystick Y", "Target X", "Target Y", "Error"])
            writer.writerows(motor_data)

        with open(cog_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Correct Answer", "Selected", "Correct", "Reaction Time"])
            writer.writerows(cognitive_data)

        print(f"[✔] Saved motor data to: {motor_file}")
        print(f"[✔] Saved cognitive data to: {cog_file}")
    else:
        print("[ℹ] Data not saved.")

if __name__ == "__main__":
    run_dual_task_mcq()
