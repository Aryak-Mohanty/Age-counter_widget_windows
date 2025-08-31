import tkinter as tk
from datetime import datetime
import win32gui
import win32con
import json
import os

CONFIG_FILE = "age_widget_config.json"

class DesktopWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Age Counter Desktop Gadget")
        self.root.overrideredirect(True)   # no titlebar
        self.root.attributes("-alpha", 0.9)  # transparency
        self.root.configure(bg="black")

        # Label for age
        self.label = tk.Label(root, font=("Arial", 16, "bold"), fg="lime", bg="black")
        self.label.pack(padx=15, pady=10)

        # Your DOB
        self.dob = datetime(2002, 5, 1)

        # Enable dragging
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Save Position", command=self.save_position)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.root.quit)
        self.root.bind("<Button-3>", self.show_menu)

        # Attach to desktop background
        self.set_parent_to_desktop()

        # Load saved position
        self.load_position()

        # Start updating age
        self.update_age()

    def set_parent_to_desktop(self):
        """Attach widget window to the Windows desktop background (WorkerW)."""
        progman = win32gui.FindWindow("Progman", None)
        win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

        # Find WorkerW
        workerw = []
        def enum_handler(hwnd, lparam):
            if win32gui.GetClassName(hwnd) == "WorkerW":
                workerw.append(hwnd)
        win32gui.EnumWindows(enum_handler, None)

        hwnd = win32gui.FindWindow(None, self.root.title())
        if hwnd and workerw:
            win32gui.SetParent(hwnd, workerw[0])  # attach to WorkerW

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    def save_position(self):
        """Save widget position to config file."""
        geom = self.root.geometry()
        pos = geom.split("+")[1:]  # ['X','Y']
        config = {"x": int(pos[0]), "y": int(pos[1])}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        print("Position saved:", config)

    def load_position(self):
        """Load saved position if exists."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            x, y = config.get("x", 100), config.get("y", 100)
            self.root.geometry(f"+{x}+{y}")
            print("Loaded position:", config)
        else:
            # Default position
            self.root.geometry("+100+100")

    def show_menu(self, event):
        """Show right-click menu."""
        self.menu.post(event.x_root, event.y_root)

    def update_age(self):
        now = datetime.now()
        years = (now - self.dob).total_seconds() / (60 * 60 * 24 * 365.2425)
        self.label.config(text=f"Age: {years:.6f}")
        self.root.after(100, self.update_age)


if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopWidget(root)
    root.mainloop()
