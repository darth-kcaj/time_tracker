import tkinter as tk
from tkinter import ttk, messagebox
from tracker_logic import TimeTrackerLogic # Import the new logic module

class TimeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.geometry("350x350") # More compact window
        self.root.resizable(False, False) # Keep it non-resizable for simplicity
        self.root.attributes('-topmost', True) # Keep window on top
        
        # Time tracking variables (now mostly managed by logic, but GUI needs access)
        self.time_var = tk.StringVar(value="00:00:00")
        self.task_name_var = tk.StringVar()
        self.project_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to track time")

        # Initialize the core logic
        self.logic = TimeTrackerLogic()
        self.logic.set_callbacks(
            update_time_cb=lambda time_str: self.root.after(0, self.time_var.set, time_str),
            update_status_cb=self.status_var.set,
            show_warning_cb=messagebox.showwarning,
            show_error_cb=messagebox.showerror
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=10) # Reduced horizontal padding
        self.root.grid_columnconfigure(0, weight=1) # Allow main frame to expand horizontally
        self.root.grid_rowconfigure(0, weight=1) # Allow main frame to expand vertically
        
        # Configure main_frame columns for centering
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Task name input
        ttk.Label(main_frame, text="Task Name:").grid(row=0, column=0, sticky=tk.EW, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.task_name_var, width=30).grid(row=1, column=0, columnspan=2, sticky=(tk.EW), pady=(0, 10)) # More compact entry, sticky EW
        
        # Project name input
        ttk.Label(main_frame, text="Project Name:").grid(row=2, column=0, sticky=tk.EW, pady=(0, 5))
        self.project_combobox = ttk.Combobox(main_frame, textvariable=self.project_name_var, width=28) # More compact combobox, sticky EW
        self.project_combobox.grid(row=3, column=0, columnspan=2, sticky=(tk.EW), pady=(0, 10)) # Sticky EW
        self.project_combobox["values"] = self.logic.get_unique_projects()
        self.project_combobox.set("") # Set initial value to empty
        
        # Time display
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10)) # Sticky EW
        ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT, pady=(10, 0)) # Add vertical padding
        ttk.Label(time_frame, textvariable=self.time_var, font=("Helvetica", 24, "bold")).pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0)) # Larger, bold font
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(10, 20)) # More vertical padding for buttons, sticky EW
        
        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_timer_gui)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5) # Add internal padding
        
        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause_timer_gui, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10), ipadx=10, ipady=5) # Add internal padding
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_timer_gui, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, ipadx=10, ipady=5) # Add internal padding
        
        # Status label
        ttk.Label(main_frame, textvariable=self.status_var, foreground="gray", font=("Helvetica", 10, "italic")).grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0)) # Italic status, sticky EW
        
    def start_timer_gui(self):
        task_name = self.task_name_var.get()
        project_name = self.project_name_var.get()
        
        self.logic.start_timer(task_name, project_name)
        
        # Update GUI based on logic state
        if self.logic.is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.start_btn.config(text="Start") # Ensure text is "Start" when starting fresh
        elif self.logic.is_paused: # This case should not happen if logic.start_timer was called
            pass # Logic handles status update
    
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
        self.logic.stop_timer(task_name, project_name)
        
        # Update GUI based on logic state
        if not self.logic.is_running:
            self.time_var.set("00:00:00")
            self.start_btn.config(state=tk.NORMAL, text="Start")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            # Clear task and project fields if desired
            # self.task_name_var.set("")
            # self.project_name_var.set("")
    
    def run(self):
        self.root.mainloop()

def main():
    app = TimeTracker()
    app.run()

if __name__ == "__main__":
    main()
