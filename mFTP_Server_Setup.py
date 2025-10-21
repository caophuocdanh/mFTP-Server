import os
import sys
import shutil
import subprocess
import winreg
import time
from colorama import Fore, Style, init # Added for colored output

init() # Initialize Colorama

APP_NAME = "mFTP Server"
EXE_NAME = "mFTP.exe"
INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], "mFTP")
SCHEDULED_TASK_NAME = "mFTP_Server_Startup"

# Helper functions for console output formatting
def print_separator(char='-', length=60, color=Style.RESET_ALL):
    print(f"{color}{char * length}{Style.RESET_ALL}")

def print_title(title, length=60, color=Fore.CYAN):
    padding = (length - len(title) - 2) // 2
    print_separator(color=color)
    print(f"{color}|{' ' * padding}{title}{' ' * (length - len(title) - 2 - padding)}|{Style.RESET_ALL}")
    print_separator(color=color)

def print_message(message, indent=0, color=Style.RESET_ALL):
    print(f"{' ' * indent}{color}{message}{Style.RESET_ALL}")

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

def run_as_admin(script_path, args):
    if not is_admin():
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}" {args}', None, 1)
        sys.exit(0)

def install_app():
    print_title(f"CÀI ĐẶT / CẬP NHẬT {APP_NAME.upper()}", color=Fore.CYAN)

    if not is_admin():
        print_message("Cần quyền quản trị để cài đặt. Đang khởi động lại với quyền quản trị...", indent=4, color=Fore.YELLOW)
        run_as_admin(sys.argv[0], "install")
        return

    print_message(f"Đang cố gắng dừng các tiến trình {EXE_NAME} đang chạy...", indent=4, color=Fore.WHITE)
    try:
        subprocess.run(['taskkill', '/f', '/im', EXE_NAME], capture_output=True)
        print_message(f"  - Đã cố gắng dừng {EXE_NAME}.", indent=4, color=Fore.GREEN)
        time.sleep(2) # Add a small delay to ensure process terminates
    except Exception as e:
        print_message(f"  - Không thể dừng {EXE_NAME}: {e}", indent=4, color=Fore.YELLOW)

    print_message(f"Kiểm tra và tạo thư mục cài đặt:", indent=4, color=Fore.WHITE)
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
        print_message(f"  - Đã tạo thư mục: {INSTALL_DIR}", indent=4, color=Fore.GREEN)
    else:
        print_message(f"  - Thư mục cài đặt đã tồn tại: {INSTALL_DIR}", indent=4, color=Fore.WHITE)

    SCAN_DIR = "C:\\SCAN"
    print_message(f"Kiểm tra và tạo thư mục SCAN:", indent=4, color=Fore.WHITE)
    if not os.path.exists(SCAN_DIR):
        try:
            os.makedirs(SCAN_DIR)
            print_message(f"  - Đã tạo thư mục: {SCAN_DIR}", indent=4, color=Fore.GREEN)
        except OSError as e:
            print_message(f"  - Lỗi khi tạo thư mục {SCAN_DIR}: {e}", indent=4, color=Fore.RED)
            print_message(f"  - Vui lòng đảm bảo bạn có quyền tạo thư mục tại {SCAN_DIR}.", indent=4, color=Fore.YELLOW)
            return
    else:
        print_message(f"  - Thư mục SCAN đã tồn tại: {SCAN_DIR}", indent=4, color=Fore.WHITE)

    destination_exe_path = os.path.join(INSTALL_DIR, EXE_NAME)

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundled_mftp_exe_path = os.path.join(sys._MEIPASS, EXE_NAME)
    else:
        bundled_mftp_exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), EXE_NAME)

    if not os.path.exists(bundled_mftp_exe_path):
        print_message(f"Lỗi: Không tìm thấy {EXE_NAME} trong gói cài đặt hoặc thư mục hiện tại.", indent=4, color=Fore.RED)
        return

    print_message(f"Sao chép {EXE_NAME} đến thư mục cài đặt...", indent=4, color=Fore.WHITE)
    shutil.copy2(bundled_mftp_exe_path, destination_exe_path)
    print_message(f"  - Đã sao chép {EXE_NAME} đến {INSTALL_DIR}", indent=4, color=Fore.GREEN)

    print_message(f"Thiết lập tác vụ lên lịch...", indent=4, color=Fore.WHITE)
    try:
        subprocess.run(['schtasks', '/delete', '/tn', SCHEDULED_TASK_NAME, '/f'], capture_output=True)
        schtasks_cmd = [
            'schtasks', '/create', '/tn', SCHEDULED_TASK_NAME,
            '/tr', f'"{destination_exe_path}"', # Explicitly add quotes for schtasks
            '/sc', 'ONLOGON', '/rl', 'HIGHEST', '/f'
        ]
        subprocess.run(schtasks_cmd, check=True, capture_output=True)
        print_message(f"  - Đã tạo tác vụ '{SCHEDULED_TASK_NAME}' để chạy khi đăng nhập.", indent=4, color=Fore.GREEN)
        subprocess.run(['schtasks', '/run', '/tn', SCHEDULED_TASK_NAME], check=True, capture_output=True)
        print_message(f"  - Đã chạy tác vụ '{SCHEDULED_TASK_NAME}' ngay lập tức.", indent=4, color=Fore.GREEN)
    except subprocess.CalledProcessError as e:
        print_message(f"  - Lỗi khi tạo tác vụ: {e}", indent=4, color=Fore.RED)
        print_message(f"  - Stdout: {e.stdout.decode()}", indent=4, color=Fore.RED)
        print_message(f"  - Stderr: {e.stderr.decode()}", indent=4, color=Fore.RED)
        print_message(f"  - Vui lòng đảm bảo bạn chạy trình cài đặt với quyền quản trị.", indent=4, color=Fore.YELLOW)
        shutil.rmtree(INSTALL_DIR)
        return

    print_separator(color=Fore.GREEN)
    print_message(f"Cài đặt {APP_NAME} hoàn tất!", indent=4, color=Fore.GREEN)
    print_separator(color=Fore.GREEN)

def uninstall_app():
    print_title(f"GỠ CÀI ĐẶT {APP_NAME.upper()}", color=Fore.CYAN)

    if not is_admin():
        print_message("Cần quyền quản trị để gỡ cài đặt. Đang khởi động lại với quyền quản trị...", indent=4, color=Fore.YELLOW)
        run_as_admin(sys.argv[0], "uninstall")
        return

    print_message(f"Đang cố gắng dừng tiến trình {EXE_NAME}...", indent=4, color=Fore.WHITE)
    try:
        subprocess.run(['taskkill', '/f', '/im', EXE_NAME], capture_output=True)
        print_message(f"  - Đã cố gắng dừng {EXE_NAME}.", indent=4, color=Fore.GREEN)
        time.sleep(2) # Add a small delay to ensure process terminates
    except Exception as e:
        print_message(f"  - Không thể dừng {EXE_NAME}: {e}", indent=4, color=Fore.YELLOW)

    print_message(f"Đang xóa tác vụ lên lịch...", indent=4, color=Fore.WHITE)
    try:
        result = subprocess.run(['schtasks', '/delete', '/tn', SCHEDULED_TASK_NAME, '/f'], capture_output=True, text=True)
        if result.returncode == 0:
            print_message(f"  - Đã xóa tác vụ '{SCHEDULED_TASK_NAME}'.", indent=4, color=Fore.GREEN)
        elif result.returncode == 1 and "ERROR: The specified task name \"mFTP_Server_Startup\" does not exist." in result.stderr:
            print_message(f"  - Tác vụ '{SCHEDULED_TASK_NAME}' không tồn tại. Không cần xóa.", indent=4, color=Fore.YELLOW)
        else:
            print_message(f"  - Không thể xóa tác vụ lên lịch '{SCHEDULED_TASK_NAME}': {result.stderr.strip()}", indent=4, color=Fore.YELLOW)
    except Exception as e:
        print_message(f"  - Lỗi khi cố gắng xóa tác vụ lên lịch '{SCHEDULED_TASK_NAME}': {e}", indent=4, color=Fore.YELLOW)

    print_message(f"Đang xóa tệp cấu hình khỏi System32...", indent=4, color=Fore.WHITE)
    SYSTEM32_CONFIG_PATH = "C:\\Windows\\System32\\config.json"
    if os.path.exists(SYSTEM32_CONFIG_PATH):
        try:
            os.remove(SYSTEM32_CONFIG_PATH)
            print_message(f"  - Đã xóa tệp cấu hình", indent=4, color=Fore.GREEN)
        except OSError as e:
            print_message(f"  - Lỗi khi xóa tệp cấu hình {SYSTEM32_CONFIG_PATH}: {e}", indent=4, color=Fore.RED)
            print_message(f"  - Vui lòng đảm bảo bạn có quyền xóa tệp tại {SYSTEM32_CONFIG_PATH}.", indent=4, color=Fore.YELLOW)
    else:
        print_message(f"  - Tệp cấu hình {SYSTEM32_CONFIG_PATH} không tồn tại. Không cần xóa.", indent=4, color=Fore.WHITE)

    print_message(f"Đang xóa thư mục cài đặt...", indent=4, color=Fore.WHITE)
    if os.path.exists(INSTALL_DIR):
        max_retries = 5
        for i in range(max_retries):
            try:
                shutil.rmtree(INSTALL_DIR)
                print_message(f"  - Đã xóa thư mục cài đặt: {INSTALL_DIR}", indent=4, color=Fore.GREEN)
                break # Exit loop if successful
            except OSError as e:
                if i < max_retries - 1:
                    print_message(f"  - Thử lại xóa thư mục ({i+1}/{max_retries}): {e}. Đang chờ...", indent=4, color=Fore.YELLOW)
                    time.sleep(1) # Wait before retrying
                else:
                    print_message(f"  - Lỗi khi xóa thư mục {INSTALL_DIR} sau {max_retries} lần thử: {e}. Vui lòng đảm bảo không có tệp nào đang được sử dụng.", indent=4, color=Fore.RED)
    else:
        print_message(f"  - Thư mục cài đặt {INSTALL_DIR} không tồn tại.", indent=4, color=Fore.YELLOW)

    print_separator(color=Fore.GREEN)
    print_message(f"Gỡ cài đặt {APP_NAME} hoàn tất!", indent=4, color=Fore.GREEN)
    print_separator(color=Fore.GREEN)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_app()
        elif sys.argv[1] == "uninstall":
            uninstall_app()
        else:
            print(f"{Fore.RED}Đối số không hợp lệ. Sử dụng 'install' hoặc 'uninstall'.{Style.RESET_ALL}")
        return

    while True:
        print_separator(char='=', color=Fore.LIGHTGREEN_EX)
        print_title(f"{APP_NAME} TRÌNH CÀI ĐẶT", color=Fore.LIGHTGREEN_EX)
        print_separator(char='=', color=Fore.LIGHTGREEN_EX)
        print_message("1. Cài đặt / Cập nhật", indent=4, color=Fore.WHITE)
        print_message("2. Gỡ cài đặt", indent=4, color=Fore.WHITE)
        print_message("3. Thoát", indent=4, color=Fore.WHITE)
        print_separator(char='-', color=Fore.LIGHTGREEN_EX)

        choice = input(f"{Fore.MAGENTA}Chọn một tùy chọn: {Style.RESET_ALL}")

        if choice == '1':
            os.system('cls') # Clear screen before installation logs
            install_app()
        elif choice == '2':
            os.system('cls') # Clear screen before uninstallation logs
            uninstall_app()
        elif choice == '3':
            print_message("Đang thoát trình cài đặt.", indent=4, color=Fore.CYAN)
            break
        else:
            print_message("Lựa chọn không hợp lệ. Vui lòng thử lại.", indent=4, color=Fore.RED)

if __name__ == "__main__":
    main()