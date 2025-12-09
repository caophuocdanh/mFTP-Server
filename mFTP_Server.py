import os
import socket
import threading
import json
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk
from pystray import MenuItem as item, Icon
import sys

# --- LOGIC MÃ HÓA ---
try:
    import win32crypt
    from win32con import CRYPTPROTECT_LOCAL_MACHINE
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

# --- LOGIC FTP SERVER ---
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

ftp_server_instance = None

def encrypt_data(data):
    if not IS_WINDOWS: return data
    return win32crypt.CryptProtectData(data.encode('utf-8'), None, None, None, None, CRYPTPROTECT_LOCAL_MACHINE)

def decrypt_data(encrypted_data):
    if not IS_WINDOWS: return encrypted_data
    return win32crypt.CryptUnprotectData(encrypted_data, None, None, None, CRYPTPROTECT_LOCAL_MACHINE)[1].decode('utf-8')

def run_ftp_server(host, port, user, password, directory, app_callback):
    global ftp_server_instance
    try:
        authorizer = DummyAuthorizer()
        authorizer.add_user(user, password, directory, perm="elradfmwMT")
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.banner = "mFTP Server Ready."
        ftp_server_instance = FTPServer((host, port), handler)
        ftp_server_instance.serve_forever()
    except Exception as e:
        print(f"Server Error: {e}")
    finally:
        app_callback.server_did_stop()

def stop_ftp_server():
    global ftp_server_instance
    if ftp_server_instance:
        ftp_server_instance.close_all()
        ftp_server_instance = None

# --- GUI ---
class FTPServerApp:
    def __init__(self, root, start_minimized=False):
        self.root = root
        self.root.title("mFTP Server Config v2.0") # Update title
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.root.resizable(False, False)

        self.config_dir = os.path.join(os.environ.get('PROGRAMDATA', 'C:/ProgramData'), 'mFTP')
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.server_running = False
        
        self.create_widgets()
        
        if not os.access(self.config_dir, os.W_OK):
             tk.Label(self.frame, text="Warning: No write access to config.", fg="red").grid(row=7, columnspan=3)

        self.load_config_and_autostart()
        
        if start_minimized:
            self.root.withdraw() 
        
    def create_widgets(self):
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        def add_field(label, row, show=None):
            tk.Label(self.frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(self.frame, show=show)
            entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW)
            return entry

        self.ip_var = tk.StringVar(value=self.get_local_ip())
        tk.Label(self.frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self.frame, textvariable=self.ip_var, state="readonly").grid(row=0, column=1, columnspan=2, sticky=tk.EW)
        
        self.port_entry = add_field("Port:", 1)
        self.user_entry = add_field("Username:", 2)
        self.pass_entry = add_field("Password:", 3, show="*")
        
        tk.Label(self.frame, text="Directory:").grid(row=4, column=0, sticky=tk.W)
        self.dir_entry = tk.Entry(self.frame)
        self.dir_entry.grid(row=4, column=1, sticky=tk.EW)
        self.browse_btn = tk.Button(self.frame, text="...", command=self.browse_dir, width=3)
        self.browse_btn.grid(row=4, column=2, padx=(5,0))

        self.action_btn = tk.Button(self.frame, text="Start Server", command=self.toggle_server)
        self.action_btn.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.frame.columnconfigure(1, weight=1)

        # UPDATE VERSION LABEL HERE
        version_label = tk.Label(self.frame, text="mFTP ver2.0 by @danhcp", fg="gray", font=("Arial", 8))
        version_label.grid(row=6, column=0, columnspan=3, pady=(5, 0))

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except: return "127.0.0.1"

    def browse_dir(self):
        d = filedialog.askdirectory()
        if d: 
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, d)

    def load_config_and_autostart(self):
        defaults = {"port": "2121", "user": "scan", "password": "123", "dir": "C:\\SCAN"}
        data = defaults.copy()
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'rb') as f:
                    content = f.read()
                    if content:
                        data.update(json.loads(decrypt_data(content)))
            except Exception as e:
                print(f"Config load error: {e}")

        self.port_entry.insert(0, data["port"])
        self.user_entry.insert(0, data["user"])
        self.pass_entry.insert(0, data["password"])
        self.dir_entry.insert(0, data["dir"])
        
        self.root.after(100, self.toggle_server)

    def toggle_server(self):
        if self.server_running:
            stop_ftp_server()
        else:
            port = self.port_entry.get()
            user = self.user_entry.get()
            pwd = self.pass_entry.get()
            dire = self.dir_entry.get()

            if not os.path.isdir(dire):
                try: os.makedirs(dire, exist_ok=True)
                except: 
                    messagebox.showerror("Error", f"Cannot create/access directory: {dire}")
                    return

            try:
                config = {"port": port, "user": user, "password": pwd, "dir": dire}
                encrypted = encrypt_data(json.dumps(config))
                with open(self.config_file, 'wb') as f: f.write(encrypted)
            except Exception as e:
                print(f"Save config failed: {e}")

            self.server_running = True
            self.update_ui()
            
            t = threading.Thread(target=run_ftp_server, args=("0.0.0.0", int(port), user, pwd, dire, self), daemon=True)
            t.start()

    def server_did_stop(self):
        self.server_running = False
        self.root.after(0, self.update_ui)

    def update_ui(self):
        state = "disabled" if self.server_running else "normal"
        self.action_btn.config(text="Stop Server" if self.server_running else "Start Server")
        for w in [self.port_entry, self.user_entry, self.pass_entry, self.dir_entry, self.browse_btn]:
            w.config(state=state)

    def hide_window(self): self.root.withdraw()
    def show_window(self): 
        self.root.deiconify()
        self.root.lift()
    def quit_app(self, icon, item):
        stop_ftp_server()
        icon.stop()
        self.root.quit()

def setup_tray(app):
    image = Image.new('RGB', (64, 64), color='green')
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill='white')
    
    if getattr(sys, 'frozen', False):
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        if os.path.exists(icon_path): image = Image.open(icon_path)
    elif os.path.exists("icon.ico"):
        image = Image.open("icon.ico")

    menu = (item('Show Config', lambda: app.show_window(), default=True), item('Quit', app.quit_app))
    Icon("mFTP", image, "mFTP Server", menu).run()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        if getattr(sys, 'frozen', False): icon_p = os.path.join(sys._MEIPASS, "icon.ico")
        else: icon_p = "icon.ico"
        if os.path.exists(icon_p): root.iconphoto(True, ImageTk.PhotoImage(Image.open(icon_p)))
    except: pass

    start_minimized = "-minimized" in sys.argv
    app = FTPServerApp(root, start_minimized=start_minimized)
    threading.Thread(target=setup_tray, args=(app,), daemon=True).start()
    root.mainloop()