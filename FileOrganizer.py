import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Optional, Set, List, Tuple

current_mode = "dark"  # define at module level
last_moves = []  # to keep track of last moves
exclude_list: Set[str] = set()
log_path = os.path.join(os.path.expanduser("~"), "FileOrganizer_log.txt")  # Default log location


def organizer(directory: str) -> None:
    global last_moves
    last_moves = []  # reset last moves
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files = [f for f in files if f not in exclude_list]  # Filter out excluded files

    # Set progress bar to processing style
    progress.config(style="processing.Horizontal.TProgressbar")
    progress['maximum'] = len(files)
    progress['value'] = 0

    with open(log_path, "a") as log:
        for idx, filename in enumerate(files):
            try:
                filepath = os.path.join(directory, filename)
                ext = os.path.splitext(filename)[1][1:] or 'No Extension'
                ts = os.path.getctime(filepath)
                date = datetime.fromtimestamp(ts).strftime('%m-%d-%Y')
                target_dir = os.path.join(directory, ext, date)
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, filename)
                shutil.move(filepath, target_path)
                last_moves.append((target_path, filepath))
                log.write(f"Moved {filepath} -> {target_path}\n")
                progress['value'] = idx + 1
                root.update_idletasks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move {filename}: {e}")
                continue

    # Restore original style based on current mode
    progress.config(style=f"{current_mode}.Horizontal.TProgressbar")


def selected_folder() -> None:
    directory = filedialog.askdirectory(title="Select Folder to Organize")
    if directory:
        get_excludes(directory)  # Get exclusions before organizing
        organizer(directory)  # Always organize, regardless of exclude_list content
        messagebox.showinfo("Success", "Files Organized")

def get_excludes(directory: str) -> None:
    global exclude_list
    exclude_list.clear()  # Start with an empty exclude list
    exclude_str = simpledialog.askstring("Exclude",
                                         "Enter file/folder names to exclude (comma separated):\n(Leave blank to organize all files)")

    if exclude_str:  # Only update exclude_list if input is provided
        exclude_list = set(
            name.strip() for name in exclude_str.split(","))  # If pressed OK with no input, exclude_list remains empty


def undo_last() -> None:
    if not last_moves:
        messagebox.showinfo("Undo", "Nothing to undo.")
        return

    folders_to_check = set()  # To track folders that may need to be removed

    with open(log_path, "a") as log:
        for src, dest in reversed(last_moves):
            try:
                shutil.move(src, dest)  # Move back to original location
                folder_path = os.path.dirname(src)  # Get the folder path that might need deletion
                folders_to_check.add(folder_path)
                log.write(f"Undo: {src} -> {dest}\n")
                parent_folder = os.path.dirname(src)  # Parent folder to check for removal
                folders_to_check.add(parent_folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to undo: {e}")
                continue

        # Remove all created folders (including extension folders) if empty
        for folder in sorted(folders_to_check, key=lambda x: len(x), reverse=True):
            try:
                if os.path.exists(folder) and not os.listdir(folder):
                    extension_folder = os.path.dirname(folder)
                    os.rmdir(folder)
                    log.write(f"Removed empty folder: {folder}\n")

                    # Also try to remove the extension folder if it's now empty
                    if (os.path.exists(extension_folder) and
                            not os.listdir(extension_folder) and
                            os.path.basename(extension_folder) != os.path.basename(os.path.dirname(src))):
                        os.rmdir(extension_folder)
                        log.write(f"Removed empty extension folder: {extension_folder}\n")
            except Exception as e:
                log.write(f"Failed to remove folder {folder}: {e}\n")
                continue

    messagebox.showinfo("Undo", "Last organize undone.")
    last_moves.clear()


def set_log_location() -> None:
    global log_path
    new_path = filedialog.asksaveasfilename(
        title="Select Log File Location",
        defaultextension=".txt",
        initialfile="FileOrganizer_log.txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if new_path:
        log_path = new_path
        messagebox.showinfo("Success", f"Log file location set to:\n{log_path}")


# Color set
def set_mode(mode: str) -> None:
    if mode == "dark":
        root.configure(bg="#222222")
        for btn_widget in [select_btn, undo_btn, log_btn]:
            btn_widget.configure(bg="#333333", fg="#ffffff")
        theme_btn.configure(bg="#333333", fg="#ffffff")
        style.configure("dark.Horizontal.TProgressbar", troughcolor='#222222', background='#333333')
    else:
        root.configure(bg="#f0f0f0")
        for btn_widget in [select_btn, undo_btn, log_btn]:
            btn_widget.configure(bg="#e0e0e0", fg="#000000")
        theme_btn.configure(bg="#e0e0e0", fg="#000000")
        style.configure("light.Horizontal.TProgressbar", troughcolor='#f0f0f0', background="#e0e0e0")

    # Update the progress bar style based on current mode
    progress['style'] = f"{mode}.Horizontal.TProgressbar"


# Color toggle
def toggle_mode() -> None:
    global current_mode
    current_mode = "light" if current_mode == "dark" else "dark"
    set_mode(current_mode)


# Initialize the Tkinter root window
root = tk.Tk()
root.title("V6nn's File Organizer")
root.geometry("350x150")  # Slightly wider for theme button

if os.name == 'nt':
    try:
        root.iconbitmap('E:\\fuck yeah\FileOrganizer v2\\assets\\v2fst.ico')  # Replace with your icon path
    except Exception as e:
        print(f"Could not load icon: {e}")

# Initialize the style for the progress bar
style = ttk.Style()
style.theme_use('default')

# Configure progress bar styles
style.configure("dark.Horizontal.TProgressbar", troughcolor='#222222', background='#333333', thickness=20)
style.configure("light.Horizontal.TProgressbar", troughcolor='#f0f0f0', background='#e0e0e0', thickness=20)
style.configure("processing.Horizontal.TProgressbar",
                troughcolor='#f0f0f0' if current_mode == 'light' else '#222222',
                background='#4CAF50',  # Green color
                thickness=20)

# Theme button in top right corner
theme_btn = tk.Button(root, text="☀", command=toggle_mode, font=("Arial", 12),
                      borderwidth=0, highlightthickness=0)
theme_btn.place(relx=0.95, rely=0.03, anchor="ne")

# UI Elements
select_btn = tk.Button(root, text="Select Folder", command=selected_folder, bg='#333333', fg='#ffffff')
select_btn.pack(pady=5)

undo_btn = tk.Button(root, text="Undo Last Organize", command=undo_last, bg='#333333', fg='#ffffff')
undo_btn.pack(pady=5)

log_btn = tk.Button(root, text="Select Log File Location", command=set_log_location, bg='#333333', fg='#ffffff')
log_btn.pack(pady=5)

# Progress bar at the bottom
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate",
                           style="dark.Horizontal.TProgressbar")
progress.pack(pady=10, side="bottom")

set_mode(current_mode)
root.mainloop()
