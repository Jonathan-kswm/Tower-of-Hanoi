import tkinter as tk
from tkinter import ttk
import time

CANVAS_W = 800
CANVAS_H = 450
PEG_POSITIONS = [200, 400, 600]
PEG_HEIGHT = 280
BASE_Y = 380
DISK_HEIGHT = 28
MAX_DISK_W = 160
MIN_DISK_W = 40
COLORS = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
    "#1abc9c", "#3498db", "#9b59b6", "#e91e63",
    "#ff5722", "#795548",
]


def disk_width(disk_num, total):
    ratio = disk_num / total
    return int(MIN_DISK_W + ratio * (MAX_DISK_W - MIN_DISK_W))


def generate_moves(n, source, target, aux, moves):
    if n == 0:
        return
    generate_moves(n - 1, source, aux, target, moves)
    moves.append((source, target))
    generate_moves(n - 1, aux, target, source, moves)


class HanoiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tower of Hanoi")
        self.root.resizable(False, False)

        self.num_disks = tk.IntVar(value=4)
        self.speed = tk.DoubleVar(value=0.5)
        self.running = False
        self.after_id = None

        self._build_ui()
        self.reset()

    def _build_ui(self):
        ctrl = tk.Frame(self.root, pady=6)
        ctrl.pack(fill=tk.X)

        tk.Label(ctrl, text="Disks:").pack(side=tk.LEFT, padx=(10, 2))
        tk.Spinbox(ctrl, from_=2, to=10, width=3, textvariable=self.num_disks).pack(side=tk.LEFT)

        tk.Label(ctrl, text="  Speed:").pack(side=tk.LEFT, padx=(10, 2))
        ttk.Scale(ctrl, from_=0.05, to=1.5, variable=self.speed,
                  orient=tk.HORIZONTAL, length=120).pack(side=tk.LEFT)
        tk.Label(ctrl, text="(slow→fast)").pack(side=tk.LEFT, padx=(2, 10))

        self.start_btn = tk.Button(ctrl, text="Start", width=8, command=self.toggle)
        self.start_btn.pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Reset", width=8, command=self.reset).pack(side=tk.LEFT, padx=4)

        self.status = tk.StringVar(value="Move: 0 / 0")
        tk.Label(ctrl, textvariable=self.status, font=("Courier", 11)).pack(side=tk.RIGHT, padx=14)

        self.canvas = tk.Canvas(self.root, width=CANVAS_W, height=CANVAS_H, bg="#1e1e2e")
        self.canvas.pack()

    # ── state ──────────────────────────────────────────────────────────────

    def reset(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.running = False
        self.start_btn.config(text="Start")

        n = self.num_disks.get()
        self.pegs = [list(range(n, 0, -1)), [], []]
        self.total_disks = n
        self.moves = []
        generate_moves(n, 0, 2, 1, self.moves)
        self.move_index = 0
        self.status.set(f"Move: 0 / {len(self.moves)}")
        self.draw()

    # ── drawing ─────────────────────────────────────────────────────────────

    def draw(self, highlight=None):
        c = self.canvas
        c.delete("all")

        # base
        c.create_rectangle(60, BASE_Y + 2, CANVAS_W - 60, BASE_Y + 22,
                            fill="#4a4a5a", outline="")

        # pegs & labels
        for i, x in enumerate(PEG_POSITIONS):
            c.create_rectangle(x - 5, BASE_Y - PEG_HEIGHT, x + 5, BASE_Y + 2,
                                fill="#7f8c8d", outline="")
            c.create_text(x, BASE_Y + 32, text=f"Peg {i + 1}",
                          fill="#aaaacc", font=("Helvetica", 11))

        # disks
        for peg_idx, peg in enumerate(self.pegs):
            x = PEG_POSITIONS[peg_idx]
            for stack_pos, disk in enumerate(peg):
                w = disk_width(disk, self.total_disks)
                y_bottom = BASE_Y - stack_pos * DISK_HEIGHT
                y_top = y_bottom - DISK_HEIGHT + 4
                color = COLORS[(disk - 1) % len(COLORS)]
                outline = "white" if highlight and disk in highlight else color
                lw = 3 if highlight and disk in highlight else 1
                c.create_rectangle(x - w // 2, y_top, x + w // 2, y_bottom,
                                   fill=color, outline=outline, width=lw)
                c.create_text(x, (y_top + y_bottom) // 2, text=str(disk),
                              fill="white", font=("Helvetica", 10, "bold"))

    # ── animation ───────────────────────────────────────────────────────────

    def toggle(self):
        if self.move_index >= len(self.moves):
            self.reset()
            return
        self.running = not self.running
        self.start_btn.config(text="Pause" if self.running else "Resume")
        if self.running:
            self.step()

    def step(self):
        if not self.running or self.move_index >= len(self.moves):
            self.running = False
            self.start_btn.config(text="Start" if self.move_index == 0 else "Done")
            if self.move_index >= len(self.moves):
                self.status.set(f"Done! {len(self.moves)} moves")
            return

        src, dst = self.moves[self.move_index]
        disk = self.pegs[src][-1]
        self.pegs[src].pop()
        self.pegs[dst].append(disk)
        self.move_index += 1
        self.status.set(f"Move: {self.move_index} / {len(self.moves)}")
        self.draw(highlight={disk})

        delay = max(30, int((1.6 - self.speed.get()) * 500))
        self.after_id = self.root.after(delay, self.step)


if __name__ == "__main__":
    root = tk.Tk()
    HanoiApp(root)
    root.mainloop()
