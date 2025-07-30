import os
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

def organizer(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            ext = os.path.splitext(filename)[1][1:] or 'No Extension'
            ts = os.path.getctime(filepath)
            date = datetime.fromtimestamp(ts).strftime('%m-%d-%Y')
            target_dir = os.path.join(directory, ext, date)
            os.makedirs(target_dir, exist_ok=True)
            shutil.move(filepath, os.path.join(target_dir, filename))

def selected_folder():
    directory = filedialog.askdirectory(title="Select Folder to Organize")
    if directory:
        organizer(directory)
        messagebox.showinfo("Success", "Files organized")

def set_mode(mode):
    if mode == "dark":
        root.configure(bg="#222222")
        btn.configure(bg="#333333", fg="#ffffff")
        toggle_btn.configure(bg="#333333", fg="#ffffff", text="Light Mode")
    else:
        root.configure(bg="#f0f0f0")
        btn.configure(bg="#e0e0e0", fg="#000000")
        toggle_btn.configure(bg="#e0e0e0", fg="#000000", text="Dark Mode")

def toggle_mode():
    global current_mode
    current_mode = "light" if current_mode == "dark" else "dark"
    set_mode(current_mode)

root = tk.Tk()
root.title("V6nn's File Organizer")
root.geometry("300x150")
root.iconbitmap(r'E:\\fuck yeah\\FileOrganizer\\favicon.ico')

current_mode = "dark"  # Default to dark mode

btn = tk.Button(root, text="Select Folder", command=selected_folder)
btn.pack(pady=20)

toggle_btn = tk.Button(root, text="Light Mode", command=toggle_mode)
toggle_btn.pack(pady=10)

set_mode(current_mode)
root.mainloop()