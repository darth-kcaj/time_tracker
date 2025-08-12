import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
from tracker_logic import TimeTrackerLogic  # Import the new logic module


class TimeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.geometry("370x460")  # Larger to fit earnings meter
        self.root.resizable(False, False)  # Keep it non-resizable for simplicity
        self.root.attributes("-topmost", True)  # Keep window on top

        # Time tracking variables (now mostly managed by logic, but GUI needs access)
        self.time_var = tk.StringVar(value="00:00:00")
        self.task_name_var = tk.StringVar()
        self.project_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to track time")
        self.hourly_rate_var = tk.DoubleVar(value=0.0)
        self.earnings_var = tk.StringVar(value="$0.0000")

        # Initialize the core logic
        self.logic = TimeTrackerLogic()
        self.logic.set_callbacks(
            update_time_cb=lambda time_str: self.root.after(
                0, self.time_var.set, time_str
            ),
            update_status_cb=self.status_var.set,
            show_warning_cb=messagebox.showwarning,
            show_error_cb=messagebox.showerror,
        )

        # Load user settings (e.g., data file path) before building UI widgets that may depend on it
        self.settings_path = os.path.join(
            os.path.expanduser("~"), ".time_tracker_settings.json"
        )
        self._load_user_settings()

        self.setup_ui()
        # Start earnings/meter animation loop
        self._schedule_earnings_update()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=10
        )
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Configure main_frame columns for centering
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Task name input
        ttk.Label(main_frame, text="Task Name:").grid(
            row=0, column=0, sticky=tk.EW, pady=(0, 5)
        )
        ttk.Entry(main_frame, textvariable=self.task_name_var, width=30).grid(
            row=1, column=0, columnspan=2, sticky=(tk.EW), pady=(0, 10)
        )

        # Project name input
        ttk.Label(main_frame, text="Project Name:").grid(
            row=2, column=0, sticky=tk.EW, pady=(0, 5)
        )
        self.project_combobox = ttk.Combobox(
            main_frame, textvariable=self.project_name_var, width=28
        )
        self.project_combobox.grid(
            row=3, column=0, columnspan=2, sticky=(tk.EW), pady=(0, 10)
        )
        self.project_combobox["values"] = self.logic.get_unique_projects()
        self.project_combobox.set("")

        # Time display
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT, pady=(10, 0))
        ttk.Label(
            time_frame, textvariable=self.time_var, font=("Helvetica", 24, "bold")
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0))

        # Earnings meter label
        earnings_frame = ttk.Frame(main_frame)
        earnings_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 6))
        ttk.Label(earnings_frame, text="Earnings:").pack(side=tk.LEFT)
        ttk.Label(
            earnings_frame,
            textvariable=self.earnings_var,
            font=("Helvetica", 18, "bold"),
            foreground="#2a9d8f",
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Smooth progress meter (fills over each minute)
        meter_frame = ttk.Frame(main_frame)
        meter_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(0, 12))
        self.meter = ttk.Progressbar(meter_frame, mode="determinate", maximum=100)
        self.meter.pack(fill=tk.X, expand=True)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(10, 20))

        self.start_btn = ttk.Button(
            button_frame, text="Start", command=self.start_timer_gui
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5)

        self.pause_btn = ttk.Button(
            button_frame, text="Pause", command=self.pause_timer_gui, state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5)

        self.stop_btn = ttk.Button(
            button_frame, text="Stop", command=self.stop_timer_gui, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, ipadx=10, ipady=5)

        # Status label
        ttk.Label(
            main_frame,
            textvariable=self.status_var,
            foreground="gray",
            font=("Helvetica", 10, "italic"),
        ).grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))

        # Settings button on the right (below status)
        self.settings_btn = ttk.Button(
            main_frame, text="Settings", command=self.open_settings_dialog
        )
        self.settings_btn.grid(row=9, column=1, sticky=tk.E, pady=(5, 0))

    def start_timer_gui(self):
        task_name = self.task_name_var.get()
        project_name = self.project_name_var.get()

        # Sync current hourly rate into logic before starting
        try:
            self.logic.set_hourly_rate(self.hourly_rate_var.get())
        except Exception:
            self.logic.set_hourly_rate(0.0)

        self.logic.start_timer(task_name, project_name)

        # Update GUI based on logic state
        if self.logic.is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.start_btn.config(text="Start")
        elif self.logic.is_paused:
            pass

    def pause_timer_gui(self):
        self.logic.pause_timer()

        # Update GUI based on logic state
        if self.logic.is_paused:
            self.start_btn.config(state=tk.NORMAL, text="Resume")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def stop_timer_gui(self):
        task_name = self.task_name_var.get()
        project_name = self.project_name_var.get()

        # Ensure latest hourly rate is synced before saving entry
        try:
            self.logic.set_hourly_rate(self.hourly_rate_var.get())
        except Exception:
            self.logic.set_hourly_rate(0.0)

        self.logic.stop_timer(task_name, project_name)

        # Update GUI based on logic state
        if not self.logic.is_running:
            self.time_var.set("00:00:00")
            self.start_btn.config(state=tk.NORMAL, text="Start")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.earnings_var.set("$0.0000")
            # Optionally clear fields
            # self.task_name_var.set("")
            # self.project_name_var.set("")

    def _schedule_earnings_update(self):
        """High-frequency UI update for earnings and meter (smooth increments)."""
        try:
            rate = float(self.hourly_rate_var.get() or 0.0)
        except Exception:
            rate = 0.0

        # Compute elapsed seconds precisely from logic state
        elapsed_seconds = 0.0
        if self.logic.is_running:
            if self.logic.is_paused:
                elapsed_seconds = self.logic.elapsed_time.total_seconds()
            else:
                elapsed_seconds = (
                    self.logic.elapsed_time.total_seconds()
                    + (datetime.now() - self.logic.start_time).total_seconds()
                )
        else:
            # Not running; logic may have reset elapsed_time
            elapsed_seconds = (
                self.logic.elapsed_time.total_seconds()
                if getattr(self.logic, "elapsed_time", None)
                else 0.0
            )

        earned = (elapsed_seconds / 3600.0) * rate
        # Show 4 decimals and a dollar sign
        self.earnings_var.set(f"${earned:.4f}")

        # Meter: fill 0-100 over each minute for a lively animation
        minute_fraction = (elapsed_seconds % 60.0) / 60.0
        self.meter["value"] = minute_fraction * 100.0

        # Re-run ~20 times per second for smoothness
        self.root.after(50, self._schedule_earnings_update)

    # -------------------- Settings handling --------------------
    def _load_user_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r") as f:
                    settings = json.load(f)
                data_file = settings.get("data_file")
                if data_file:
                    self.logic.set_data_file(data_file)
                rate = settings.get("hourly_rate")
                if rate is not None:
                    try:
                        rate_f = float(rate)
                        self.hourly_rate_var.set(rate_f)
                        self.logic.set_hourly_rate(rate_f)
                    except Exception:
                        pass
        except Exception as e:
            # Show non-blocking error, but proceed with defaults
            print(f"Failed to load settings: {e}")

    def _save_user_settings(self):
        try:
            settings = {
                "data_file": getattr(self.logic, "data_file", None),
                "hourly_rate": float(self.hourly_rate_var.get() or 0.0),
            }
            with open(self.settings_path, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def open_settings_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.grab_set()

        frm = ttk.Frame(dialog, padding=10)
        frm.grid(row=0, column=0, sticky=tk.NSEW)
        frm.grid_columnconfigure(1, weight=1)

        ttk.Label(frm, text="Data file path:").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        path_var = tk.StringVar(value=getattr(self.logic, "data_file", ""))
        entry = ttk.Entry(frm, textvariable=path_var, width=45)
        entry.grid(row=1, column=0, columnspan=2, sticky=tk.EW)

        def browse():
            initialdir = (
                os.path.dirname(path_var.get())
                if path_var.get()
                else os.path.expanduser("~")
            )
            file_path = filedialog.asksaveasfilename(
                parent=dialog,
                title="Choose data file",
                defaultextension=".json",
                filetypes=[["JSON files", "*.json"], ["All files", "*.*"]],
                initialdir=initialdir,
                initialfile=(
                    os.path.basename(path_var.get())
                    if path_var.get()
                    else "time_tracker_data.json"
                ),
            )
            if file_path:
                path_var.set(file_path)

        browse_btn = ttk.Button(frm, text="Browse…", command=browse)
        browse_btn.grid(row=1, column=2, padx=(5, 0))

        # Hourly rate
        ttk.Label(frm, text="Hourly rate ($/hr):").grid(
            row=2, column=0, sticky=tk.W, pady=(10, 5)
        )
        rate_var = tk.StringVar(value=str(self.hourly_rate_var.get() or 0.0))
        rate_entry = ttk.Entry(frm, textvariable=rate_var, width=20)
        rate_entry.grid(row=3, column=0, sticky=tk.W)

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, sticky=tk.E, pady=(10, 0))

        def on_ok():
            chosen = path_var.get().strip()
            if not chosen:
                messagebox.showwarning("Warning", "Please enter a valid path")
                return
            self.logic.set_data_file(chosen)
            # Validate and save hourly rate
            try:
                rate_val = float(rate_var.get().strip() or 0.0)
                if rate_val < 0:
                    raise ValueError
                self.hourly_rate_var.set(rate_val)
                self.logic.set_hourly_rate(rate_val)
            except Exception:
                messagebox.showwarning(
                    "Warning", "Please enter a valid non-negative hourly rate"
                )
                return
            self._save_user_settings()
            dialog.destroy()

        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(btns, text="OK", command=on_ok).pack(side=tk.RIGHT)

    def run(self):
        self.root.mainloop()


def main():
    app = TimeTracker()
    app.run()


if __name__ == "__main__":
    main()
