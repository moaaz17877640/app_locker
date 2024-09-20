import tkinter as tk
from tkinter import messagebox
import subprocess
import psutil
import time
import threading
import os

class AppLocker:
    def __init__(self, root):
        self.root = root
        self.root.title("Application Locker")

        self.password = "admin222"  # Set your default password
        self.locked_apps = []
        self.check_thread = threading.Thread(target=self.check_running_apps, daemon=True)

        self.create_widgets()
        self.start_checking()

    def create_widgets(self):
        self.app_entry = tk.Entry(self.root, width=30)
        self.app_entry.pack(pady=10)

        self.lock_button = tk.Button(self.root, text="Lock Application", command=self.lock_app)
        self.lock_button.pack(pady=10)

        self.pass_entry = tk.Entry(self.root, show="*", width=30)
        self.pass_entry.pack(pady=10)

        self.unlock_button = tk.Button(self.root, text="Unlock Application", command=self.unlock_app)
        self.unlock_button.pack(pady=10)

    def start_checking(self):
        self.check_thread.start()

    def lock_app(self):
        app_name = self.app_entry.get()
        if app_name and app_name not in self.locked_apps:
            self.locked_apps.append(app_name)
            messagebox.showinfo("Locked", f"{app_name} has been locked.")
            self.app_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Application is already locked or invalid name.")

    def unlock_app(self):
        app_name = self.app_entry.get()
        password = self.pass_entry.get()

        if app_name in self.locked_apps:
            if password == self.password:
                self.locked_apps.remove(app_name)
                messagebox.showinfo("Unlocked", f"{app_name} has been unlocked.")
                self.app_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)

                # Launch the application if not already running
                if not self.is_app_running(app_name):
                    try:
                        subprocess.Popen(app_name, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to launch application: {e}")
            else:
                messagebox.showerror("Error", "Incorrect password!")
        else:
            messagebox.showwarning("Warning", "Application is not locked or invalid name.")

    def check_running_apps(self):
        while True:
            for app in list(self.locked_apps):
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == app:
                        self.prompt_for_password(app)
                        proc.terminate()
            time.sleep(5)

    def prompt_for_password(self, app_name):
        password_window = tk.Toplevel(self.root)
        password_window.title("Enter Password")

        tk.Label(password_window, text=f"Enter password to unlock {app_name}:").pack(pady=10)
        password_entry = tk.Entry(password_window, show="*")
        password_entry.pack(pady=10)

        def check_password():
            if password_entry.get() == self.password:
                messagebox.showinfo("Unlocked", f"{app_name} has been unlocked.")
                password_window.destroy()
                if not self.is_app_running(app_name):
                    try:
                        subprocess.Popen(app_name, creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to launch application: {e}")
                self.locked_apps.remove(app_name)
            else:
                messagebox.showerror("Error", "Incorrect password!")

        tk.Button(password_window, text="Submit", command=check_password).pack(pady=10)

    def is_app_running(self, app_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == app_name:
                return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = AppLocker(root)
    root.mainloop()