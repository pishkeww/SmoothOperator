import tkinter as tk
import subprocess

TASKS = {
    "Steady Hand Challenge": "tremor_analysis.py",
    "Precision Follow": "target_tracking.py",
    "Rapid Target Reach": "fitts_law.py",
    "Rhythmic Tap Challenge": "tapping.py",
    "Quick Start Reaction": "reaction.py",
    "Smooth Trace Challenge": "path_smoothness.py",
    "Brain & Brawn Challenge": "dual_task.py"
}

def run_task(script_name):
    subprocess.run(["python", script_name])

#
root = tk.Tk()
root.title("Smooth Operator – Parkinson’s Task Suite")
root.geometry("450x550")
root.configure(bg="#eef2f3")
#
TITLE_FONT = ("Helvetica", 20, "bold")
LABEL_FONT = ("Helvetica", 14)
BUTTON_FONT = ("Helvetica", 12)
BUTTON_COLOR = "#4CAF50"
BUTTON_HOVER = "#45a049"
EXIT_COLOR = "#e57373"
#
tk.Label(root, text="🎮 Smooth Operator", font=TITLE_FONT, bg="#eef2f3", fg="#333").pack(pady=30)
tk.Label(root, text="Parkinson’s Motor & Cognitive Task Suite", font=LABEL_FONT, bg="#eef2f3", fg="#555").pack(pady=5)
#
def create_button(text, script):
    btn = tk.Button(root, text=text, font=BUTTON_FONT, width=35, height=2, bg=BUTTON_COLOR, fg="white",
                    activebackground=BUTTON_HOVER,
                    command=lambda: run_task(script))
    btn.pack(pady=8)

#
for name, script in TASKS.items():
    create_button(name, script)

#
tk.Button(root, text="Exit", font=BUTTON_FONT, width=35, height=2,
          bg=EXIT_COLOR, fg="white", activebackground="#d32f2f",
          command=root.quit).pack(pady=20)

root.mainloop()
