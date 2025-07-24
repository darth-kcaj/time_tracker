import json
import os
from datetime import datetime, timedelta
import threading
import time

class TimeTrackerLogic:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.elapsed_time = timedelta()
        self.timer_thread = None
        self.data_file = os.path.join(os.path.expanduser("~"), "time_tracker_data.json")
        self.data = []
        self.load_data()
        
        # Callbacks for GUI updates
        self.update_time_callback = None
        self.update_status_callback = None
        self.show_warning_callback = None
        self.show_error_callback = None

    def set_callbacks(self, update_time_cb, update_status_cb, show_warning_cb, show_error_cb):
        self.update_time_callback = update_time_cb
        self.update_status_callback = update_status_cb
        self.show_warning_callback = show_warning_cb
        self.show_error_callback = show_error_cb

    def start_timer(self, task_name, project_name):
        if not task_name.strip():
            if self.show_warning_callback:
                self.show_warning_callback("Warning", "Please enter a task name")
            return
            
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_time = datetime.now()
            
            status_text = f"Tracking: {task_name}"
            if project_name:
                status_text += f" (Project: {project_name})"
            if self.update_status_callback:
                self.update_status_callback(status_text)
            
            self.timer_thread = threading.Thread(target=self._update_timer_loop, daemon=True)
            self.timer_thread.start()
        elif self.is_paused:
            self.is_paused = False
            self.start_time = datetime.now() - self.elapsed_time
            if self.update_status_callback:
                self.update_status_callback("Resumed tracking")
    
    def pause_timer(self):
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.elapsed_time = datetime.now() - self.start_time
            if self.update_status_callback:
                self.update_status_callback("Timer paused")
    
    def stop_timer(self, task_name, project_name):
        if self.is_running:
            if self.is_paused:
                final_time = self.elapsed_time
            else:
                final_time = datetime.now() - self.start_time
                
            self.save_time_entry(task_name, project_name, final_time)
            
            self.is_running = False
            self.is_paused = False
            self.elapsed_time = timedelta()
            self.start_time = None
            
            if self.update_time_callback:
                self.update_time_callback("00:00:00")
            if self.update_status_callback:
                self.update_status_callback("Time entry saved")
    
    def _update_timer_loop(self):
        while self.is_running:
            if not self.is_paused:
                current_elapsed = datetime.now() - self.start_time + self.elapsed_time
                hours, remainder = divmod(int(current_elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if self.update_time_callback:
                    self.update_time_callback(time_str)
            time.sleep(0.1)
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = []
    
    def save_time_entry(self, task_name, project_name, duration):
        task_name = task_name.strip()
        project_name = project_name.strip()
        
        duration_seconds = int(duration.total_seconds())
        
        entry = {
            "task": task_name,
            "project": project_name,
            "duration_seconds": duration_seconds,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat()
        }
        
        self.data.append(entry)
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            if self.show_error_callback:
                self.show_error_callback("Error", f"Could not save data: {e}")

    def get_unique_projects(self):
        """Returns a sorted list of unique project names from the loaded data."""
        projects = set()
        for entry in self.data:
            if "project" in entry and entry["project"].strip():
                projects.add(entry["project"].strip())
        return sorted(list(projects))
