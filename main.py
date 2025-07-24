import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time

class TimeTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Tracker")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Time tracking variables
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.elapsed_time = timedelta()
        self.timer_thread = None
        
        # Data storage
        self.data_file = os.path.join(os.path.expanduser("~"), "time_tracker_data.json")
        self.load_data()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Task name input
        ttk.Label(main_frame, text="Task Name:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.task_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.task_name_var, width=30).grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Project name input
        ttk.Label(main_frame, text="Project Name:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.project_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.project_name_var, width=30).grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Time display
        self.time_var = tk.StringVar(value="00:00:00")
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT)
        ttk.Label(time_frame, textvariable=self.time_var, font=("Helvetica", 16)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2)
        
        self.start_btn = ttk.Button(button_frame, text="Start", command=self.start_timer)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_btn = ttk.Button(button_frame, text="Pause", command=self.pause_timer, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_timer, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to track time")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="gray").grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
    def start_timer(self):
        if not self.task_name_var.get().strip():
            messagebox.showwarning("Warning", "Please enter a task name")
            return
            
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_time = datetime.now()
            
            # Update button states
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.start_btn.config(text="Start") # Ensure text is "Start" when starting fresh
            
            # Update status
            task_name = self.task_name_var.get()
            project_name = self.project_name_var.get()
            status_text = f"Tracking: {task_name}"
            if project_name:
                status_text += f" (Project: {project_name})"
            self.status_var.set(status_text)
            
            # Start the timer thread
            self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()
        elif self.is_paused:
            # Resume from paused state
            self.is_paused = False
            self.start_time = datetime.now() - self.elapsed_time
            self.status_var.set("Resumed tracking")
            
            # Update button states for resuming
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.start_btn.config(text="Start") # Change text back to "Start"
    
    def pause_timer(self):
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.elapsed_time = datetime.now() - self.start_time
            self.status_var.set("Timer paused")
            
            # Update button states for pausing
            self.start_btn.config(state=tk.NORMAL, text="Resume")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
    
    def stop_timer(self):
        if self.is_running:
            # Calculate final elapsed time
            if self.is_paused:
                final_time = self.elapsed_time
            else:
                final_time = datetime.now() - self.start_time
                
            # Save the time entry
            self.save_time_entry(final_time)
            
            # Reset timer
            self.is_running = False
            self.is_paused = False
            self.elapsed_time = timedelta()
            self.start_time = None
            
            # Update UI
            self.time_var.set("00:00:00")
            self.start_btn.config(state=tk.NORMAL, text="Start")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_var.set("Time entry saved")
            
            # Clear task and project fields if desired
            # self.task_name_var.set("")
            # self.project_name_var.set("")
    
    def update_timer(self):
        while self.is_running:
            if not self.is_paused:
                current_elapsed = datetime.now() - self.start_time + self.elapsed_time
                hours, remainder = divmod(int(current_elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.root.after(0, self.time_var.set, time_str)
            time.sleep(0.1)  # Update every 100ms
    
    def load_data(self):
        """Load time tracking data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = []
    
    def save_time_entry(self, duration):
        """Save a time entry to the data file"""
        task_name = self.task_name_var.get().strip()
        project_name = self.project_name_var.get().strip()
        
        # Convert duration to seconds
        duration_seconds = int(duration.total_seconds())
        
        # Create entry
        entry = {
            "task": task_name,
            "project": project_name,
            "duration_seconds": duration_seconds,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to data
        self.data.append(entry)
        
        # Save to file
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {e}")
    
    def run(self):
        self.root.mainloop()

def main():
    app = TimeTracker()
    app.run()

if __name__ == "__main__":
    main()
