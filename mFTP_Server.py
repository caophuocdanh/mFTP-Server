import os
import socket
import threading
import json
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk # Added ImageTk
from pystray import MenuItem as item, Icon
import subprocess
import sys

# --- PHẦN MÃ HÓA ---
try:
    import win32crypt
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False
    print("WARNING: win32crypt not found. Configuration file will not be encrypted.")

# --- PHẦN LOGIC CỦA FTP SERVER ---
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

ftp_server_thread = None
ftp_server_instance = None

def encrypt_data(data):
    if not IS_WINDOWS: return data
    return win32crypt.CryptProtectData(data.encode('utf-8'), None, None, None, None, 0)

def decrypt_data(encrypted_data):
    if not IS_WINDOWS: return encrypted_data
    plaintext = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)[1]
    return plaintext.decode('utf-8')

def run_ftp_server(host, port, user, password, directory, app_callback):
    global ftp_server_instance
    try:
        authorizer = DummyAuthorizer()
        authorizer.add_user(user, password, directory, perm="elradfmwMT")
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "Simple FTP Server Ready."
        address = (host, port)
        ftp_server_instance = FTPServer(address, handler)
        print(f"FTP Server starting on {host}:{port} (listening on all interfaces)")
        ftp_server_instance.serve_forever()
        print("FTP Server has stopped serving.")
    except Exception as e:
        print(f"Error starting FTP server: {e}")
        messagebox.showerror("FTP Server Error", f"Failed to start server: {e}")
    finally:
        app_callback.server_did_stop()

def stop_ftp_server():
    global ftp_server_instance
    if ftp_server_instance:
        print("Stopping FTP server...")
        ftp_server_instance.close_all()
        ftp_server_instance = None
        # Add a small delay to allow the server to release resources
        time.sleep(0.5) # Wait for 0.5 seconds

# --- PHẦN GIAO DIỆN (GUI) VÀ KHAY HỆ THỐNG ---

class FTPServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Server Config")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.resizable(False, False) # Disallow resizing
        # self.root.geometry("400x280") # Set fixed size
        self.config_file = "config.json"
        self.server_running = False
        self.create_widgets()
        self.load_config_and_autostart()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def create_widgets(self):
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_var = tk.StringVar(value=self.get_local_ip())
        tk.Entry(self.frame, textvariable=self.ip_var, state="readonly").grid(row=0, column=1, columnspan=2, sticky=tk.EW)
        tk.Label(self.frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.port_entry = tk.Entry(self.frame)
        self.port_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW)
        tk.Label(self.frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.user_entry = tk.Entry(self.frame)
        self.user_entry.grid(row=2, column=1, columnspan=2, sticky=tk.EW)
        tk.Label(self.frame, text="Password:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.pass_entry = tk.Entry(self.frame, show="*")
        self.pass_entry.grid(row=3, column=1, columnspan=2, sticky=tk.EW)
        tk.Label(self.frame, text="Directory:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.dir_entry = tk.Entry(self.frame)
        self.dir_entry.grid(row=4, column=1, sticky=tk.EW)
        self.browse_button = tk.Button(self.frame, text="Browse...", command=self.browse_directory)
        self.browse_button.grid(row=4, column=2, padx=(5,0))
        self.action_button = tk.Button(self.frame, text="Start Server", command=self.toggle_server_state)
        self.action_button.grid(row=5, column=0, columnspan=3, pady=10)
        self.frame.columnconfigure(1, weight=1)

        # Add version label
        version_label = tk.Label(self.frame, text="Version 1.0 build-2110 ©danhcp", fg="gray", font=("Arial", 8))
        version_label.grid(row=6, column=0, columnspan=2, pady=0)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END) # Clear existing content
            self.dir_entry.insert(0, directory) # Insert new directory

    def load_config_and_autostart(self):
        config_loaded = False
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'rb') as f:
                    encrypted_config = f.read()
                    if encrypted_config:
                        decrypted_json = decrypt_data(encrypted_config)
                        config = json.loads(decrypted_json)
                        self.port_entry.insert(0, config.get("port", "2121"))
                        self.user_entry.insert(0, config.get("user", "scan"))
                        self.pass_entry.insert(0, config.get("password", "123"))
                        self.dir_entry.insert(0, config.get("dir", "C:\\SCAN"))
                        config_loaded = True
        except Exception as e:
            print(f"Could not load/decrypt config: {e}. A new one will be created.")
            if os.path.exists(self.config_file): os.remove(self.config_file)
        if not config_loaded:
            self.port_entry.insert(0, "2121")
            self.user_entry.insert(0, "scan")
            self.pass_entry.insert(0, "123")
            self.dir_entry.insert(0, "C:\\SCAN")
        if self.validate_inputs(silent=True): self.toggle_server_state()

    def update_ui_state(self):
        state = "disabled" if self.server_running else "normal"
        button_text = "Stop Server" if self.server_running else "Start Server"
        for entry in [self.port_entry, self.user_entry, self.pass_entry, self.dir_entry]:
            entry.config(state=state)
        self.browse_button.config(state=state)
        self.action_button.config(text=button_text)

    def validate_inputs(self, silent=False):
        port = self.port_entry.get()
        user = self.user_entry.get()
        password = self.pass_entry.get()
        directory = self.dir_entry.get()
        if not all([port, user, password, directory]):
            if not silent: messagebox.showerror("Error", "All fields are required!")
            return False
        if not os.path.isdir(directory):
            if not silent: messagebox.showerror("Error", f"Directory does not exist: {directory}")
            return False
        try: int(port)
        except ValueError:
            if not silent: messagebox.showerror("Error", "Port must be a number.")
            return False
        return True

    def create_or_update_firewall_rules(self, port):
        rule_names = {
            "TCP": "mFTP Server (TCP)",
            "UDP": "mFTP Server (UDP)"
        }
        try:
            for protocol, rule_name in rule_names.items():
                # 1. Xóa Rule cũ để đảm bảo Port được cập nhật
                delete_cmd = f'netsh advfirewall firewall delete rule name="{rule_name}"'
                subprocess.run(delete_cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                # 2. Thêm Rule mới với Port hiện tại
                add_cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol={protocol} localport={port}'
                print(f"Executing: {add_cmd}")
                subprocess.check_call(add_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"Firewall rules for port {port} were created/updated successfully.")
            return True  # Báo hiệu thành công

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Firewall command failed: {e}")
            messagebox.showerror(
                "Administrator Rights Required",
                "Failed to create firewall rules. This action requires administrator privileges.\n\n"
                "Please run this application as an administrator to manage firewall rules automatically.\n\n"
                "How to run as administrator:\n"
                "1. Open Start, type 'cmd'.\n"
                "2. Right-click 'Command Prompt' and select 'Run as administrator'.\n"
                "3. Navigate to your Desktop and run the script: python ftp_server_app.py"
            )
            return False # Báo hiệu thất bại

    def toggle_server_state(self):
        global ftp_server_thread
        if self.server_running:
            stop_ftp_server()
        else:
            if not self.validate_inputs(): return
            
            port_str = self.port_entry.get()
            if not self.create_or_update_firewall_rules(port_str):
                return

            config = {"port": port_str, "user": self.user_entry.get(), "password": self.pass_entry.get(), "dir": self.dir_entry.get()}
            try:
                json_string = json.dumps(config, indent=4)
                encrypted_config = encrypt_data(json_string)
                with open(self.config_file, 'wb') as f: f.write(encrypted_config)
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not save encrypted config file: {e}")
            
            self.server_running = True
            self.update_ui_state()
            ftp_server_thread = threading.Thread(
                target=run_ftp_server,
                args=("0.0.0.0", int(config["port"]), config["user"], config["password"], config["dir"], self),
                daemon=True
            )
            ftp_server_thread.start()
            # self.hide_window()

    def server_did_stop(self):
        self.server_running = False
        self.update_ui_state()

    def hide_window(self):
        self.root.withdraw()

    def show_window(self, icon, item):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, icon, item):
        stop_ftp_server()
        icon.stop()
        self.root.quit()

def create_image(width, height, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def setup_tray(app):
    icon_image = None
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        bundle_dir = sys._MEIPASS
        bundled_icon_path = os.path.join(bundle_dir, "icon.ico")
        try:
            icon_image = Image.open(bundled_icon_path)
        except FileNotFoundError:
            pass # Fallback to default if bundled icon not found or cannot be opened

    if icon_image is None:
        # If not bundled, or bundled icon not found/failed to load, use default or local file
        local_icon_path = "icon.ico"
        if os.path.exists(local_icon_path):
            icon_image = Image.open(local_icon_path)
        else:
            icon_image = create_image(64, 64, 'black', 'green')
            # Optionally save the default icon if running as script, but not necessary for bundled app
            # icon_image.save(local_icon_path)

    menu = (item('Show Config', app.show_window, default=True), item('Quit', app.quit_app))
    icon = Icon("FTP Server", icon_image, "FTP Server", menu)
    icon.run()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        icon_path = None
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # Running in a PyInstaller bundle
            bundle_dir = sys._MEIPASS
            icon_path = os.path.join(bundle_dir, "icon.ico")
        else:
            # Running as a script
            icon_path = "icon.ico" # Assuming icon.ico is in the same directory as the script

        if icon_path and os.path.exists(icon_path):
            icon_image_pil = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image_pil)
            root.iconphoto(True, icon_photo)
        else:
            print(f"WARNING: icon.ico not found at {icon_path}. Using default Tkinter icon.")
    except Exception as e:
        print(f"ERROR: Could not set title bar icon from {icon_path}: {e}")
        # Fallback to default Tkinter icon if loading fails
    app = FTPServerApp(root)
    root.withdraw()
    tray_thread = threading.Thread(target=setup_tray, args=(app,), daemon=True)
    tray_thread.start()
    root.mainloop()