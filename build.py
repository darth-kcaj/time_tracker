import PyInstaller.__main__
import os
from datetime import datetime # Import datetime for timestamp

# Generate a timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
app_name = f"TimeTracker_{timestamp}"

# Configuration for PyInstaller
pyinstaller_args = [
    'main.py',
    f'--name={app_name}', # Use the timestamped name
    '--windowed',  # No console window (since we have a GUI)
    '--onefile',   # Create a single executable file
    '--clean',     # Clean PyInstaller cache before building
    '--icon=icon.ico',  # Use an icon if available
]

# Check if icon file exists, if not, remove the icon argument
if not os.path.exists('icon.ico'):
    pyinstaller_args.remove('--icon=icon.ico')
    print("No icon file found. Building without icon.")

# Run PyInstaller
if __name__ == '__main__':
    print("Starting PyInstaller build process...")
    PyInstaller.__main__.run(pyinstaller_args)
    print("Build completed! The executable is in the 'dist' folder.")
