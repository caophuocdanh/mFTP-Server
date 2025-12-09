import os
import sys
import shutil
import subprocess
import winreg
import ctypes
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk

# --- CẤU HÌNH ---
APP_NAME = "mFTP Server"
VERSION = "2.0"
AUTHOR = "@danhcp"
EXE_NAME = "mFTP.exe"
INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], "mFTP")
CONFIG_DIR = os.path.join(os.environ.get('PROGRAMDATA', 'C:/ProgramData'), 'mFTP')
SCAN_DIR = "C:\\SCAN"
REG_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
REG_NAME = "mFTP_Server"

# --- HÀM HỆ THỐNG CƠ BẢN ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
    sys.exit(0)

# --- GIAO DIỆN CÀI ĐẶT ---
class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Setup {APP_NAME} v{VERSION}")
        self.root.geometry("480x340") # Tăng nhẹ chiều cao để chứa footer
        self.root.resizable(False, False)
        
        try:
            if getattr(sys, 'frozen', False):
                icon_path = os.path.join(sys._MEIPASS, "icon.ico")
            else:
                icon_path = "icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except: pass

        self.setup_ui()
        self.check_status()

    def setup_ui(self):
        # 1. Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=45)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Tiêu đề kèm Version
        lbl_title = tk.Label(header_frame, text=f"CÀI ĐẶT {APP_NAME.upper()} v{VERSION}", 
                             fg="white", bg="#2c3e50", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(expand=True)

        # 2. Status
        status_frame = tk.Frame(self.root, pady=5)
        status_frame.pack(fill=tk.X)
        
        self.lbl_status_key = tk.Label(status_frame, text="Trạng thái hệ thống:", font=("Segoe UI", 9))
        self.lbl_status_key.pack(side=tk.LEFT, padx=(15, 5))
        
        self.lbl_status_val = tk.Label(status_frame, text="Kiểm tra...", font=("Segoe UI", 9, "bold"))
        self.lbl_status_val.pack(side=tk.LEFT)

        # 3. Log Area
        self.log_area = scrolledtext.ScrolledText(self.root, state='disabled', height=8, font=("Consolas", 8))
        self.log_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.log_area.tag_config("INFO", foreground="black")
        self.log_area.tag_config("SUCCESS", foreground="green")
        self.log_area.tag_config("ERROR", foreground="red")
        self.log_area.tag_config("WARN", foreground="#d35400")

        # 4. Buttons
        btn_frame = tk.Frame(self.root, pady=5)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        self.btn_install = ttk.Button(btn_frame, text="Cài đặt", command=self.start_install_thread)
        self.btn_install.grid(row=0, column=0, sticky="ew", padx=2)

        self.btn_uninstall = ttk.Button(btn_frame, text="Gỡ bỏ", command=self.start_uninstall_thread)
        self.btn_uninstall.grid(row=0, column=1, sticky="ew", padx=2)

        self.btn_exit = ttk.Button(btn_frame, text="Thoát", command=self.root.quit)
        self.btn_exit.grid(row=0, column=2, sticky="ew", padx=2)

        # 5. Footer Credit
        lbl_credit = tk.Label(self.root, text=f"Developed by {AUTHOR}", fg="gray", font=("Arial", 7))
        lbl_credit.pack(side=tk.BOTTOM, pady=(0, 5))

    def check_status(self):
        exe_path = os.path.join(INSTALL_DIR, EXE_NAME)
        if os.path.exists(exe_path):
            self.lbl_status_val.config(text="ĐÃ CÀI ĐẶT", fg="green")
            self.btn_install.config(text="Cập nhật lại")
            self.btn_uninstall.state(['!disabled'])
        else:
            self.lbl_status_val.config(text="CHƯA CÀI ĐẶT", fg="#e74c3c")
            self.btn_install.config(text="Cài đặt ngay")
            self.btn_uninstall.state(['disabled'])

    def log(self, message, level="INFO"):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{level}] {message}\n", level)
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def toggle_buttons(self, state):
        s = 'normal' if state else 'disabled'
        self.btn_install.config(state=s)
        self.btn_uninstall.config(state=s)
        self.btn_exit.config(state=s)

    # --- LOGIC CÀI ĐẶT ---
    def start_install_thread(self):
        self.toggle_buttons(False)
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        try:
            self.log(f"Bắt đầu setup v{VERSION}...", "INFO")
            
            self.log("Dừng ứng dụng cũ...", "INFO")
            subprocess.run(['taskkill', '/f', '/im', EXE_NAME], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            for path in [INSTALL_DIR, CONFIG_DIR, SCAN_DIR]:
                if not os.path.exists(path):
                    os.makedirs(path)
                    self.log(f"Tạo: {path}", "INFO")

            self.log("Cấp quyền Users...", "INFO")
            try:
                subprocess.run(['icacls', CONFIG_DIR, '/grant', 'Users:(OI)(CI)F', '/T', '/C'], 
                               capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(['icacls', SCAN_DIR, '/grant', 'Users:(OI)(CI)F', '/T', '/C'], 
                               capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass

            self.log("Copy file hệ thống...", "INFO")
            if getattr(sys, 'frozen', False):
                src = os.path.join(sys._MEIPASS, EXE_NAME)
            else:
                src = os.path.join(os.path.dirname(os.path.abspath(__file__)), EXE_NAME)
            
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(INSTALL_DIR, EXE_NAME))
                self.log("Copy file OK.", "SUCCESS")
            else:
                self.log(f"Lỗi: Thiếu {EXE_NAME}", "ERROR")
                return

            self.log("Cấu hình Firewall (2121)...", "INFO")
            try:
                subprocess.run('netsh advfirewall firewall delete rule name="mFTP Server (TCP)"', 
                               shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run('netsh advfirewall firewall delete rule name="mFTP Server (UDP)"', 
                               shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run('netsh advfirewall firewall add rule name="mFTP Server (TCP)" dir=in action=allow protocol=TCP localport=2121', 
                               shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run('netsh advfirewall firewall add rule name="mFTP Server (UDP)" dir=in action=allow protocol=UDP localport=2121', 
                               shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass

            self.log("Đăng ký Startup...", "INFO")
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_SET_VALUE)
                cmd = f'"{os.path.join(INSTALL_DIR, EXE_NAME)}" -minimized'
                winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, cmd)
                winreg.CloseKey(key)
            except Exception as e:
                self.log(f"Lỗi Reg: {e}", "ERROR")

            self.log("Khởi động Service...", "INFO")
            subprocess.Popen([os.path.join(INSTALL_DIR, EXE_NAME)])
            
            self.log("CÀI ĐẶT HOÀN TẤT!", "SUCCESS")
            messagebox.showinfo("mFTP Setup", f"Đã cài đặt mFTP Server v{VERSION} thành công!")

        except Exception as e:
            self.log(f"Lỗi: {e}", "ERROR")
        finally:
            self.root.after(0, self.check_status)
            self.toggle_buttons(True)

    def start_uninstall_thread(self):
        if not messagebox.askyesno("Gỡ cài đặt", "Xóa hoàn toàn mFTP Server khỏi máy tính?"):
            return
        self.toggle_buttons(False)
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state='disabled')
        threading.Thread(target=self.run_uninstall, daemon=True).start()

    def run_uninstall(self):
        try:
            self.log("Đang dừng Service...", "INFO")
            subprocess.run(['taskkill', '/f', '/im', EXE_NAME], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

            self.log("Xóa Registry...", "INFO")
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_PATH, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, REG_NAME)
                winreg.CloseKey(key)
            except: pass
            
            subprocess.run('netsh advfirewall firewall delete rule name="mFTP Server (TCP)"', 
                           shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

            self.log("Xóa tập tin...", "INFO")
            for path in [INSTALL_DIR, CONFIG_DIR]:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                        self.log(f"Đã xóa: {path}", "SUCCESS")
                    except:
                        self.log(f"Lỗi xóa: {path}", "WARN")
            
            self.log("ĐÃ GỠ CÀI ĐẶT!", "SUCCESS")
            messagebox.showinfo("mFTP Setup", "Đã gỡ bỏ phần mềm.")

        except Exception as e:
            self.log(f"Lỗi: {e}", "ERROR")
        finally:
            self.root.after(0, self.check_status)
            self.toggle_buttons(True)

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
    else:
        root = tk.Tk()
        app = InstallerGUI(root)
        root.eval('tk::PlaceWindow . center')
        root.mainloop()