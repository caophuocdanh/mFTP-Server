# mFTP Server
<p align="center">
  <img src="app.png" alt="mFTP" width="400">
</p>

## 🧭 Giới thiệu

**mFTP Server** là một ứng dụng máy chủ FTP **đơn giản, nhẹ và thân thiện**, được thiết kế để dễ dàng chia sẻ tệp tin trong mạng cục bộ.  
Ứng dụng chạy ngầm trong **khay hệ thống (System Tray)** và cung cấp **giao diện cấu hình trực quan**.

---

## ⚙️ Chức năng chính

- **Máy chủ FTP đơn giản:** Thiết lập máy chủ FTP với tên người dùng, mật khẩu và thư mục chia sẻ tùy chỉnh.  
- **Chạy ngầm:** Ứng dụng hoạt động trong khay hệ thống, không chiếm không gian làm việc.  
- **Tự động khởi động:** Có thể cấu hình để tự động chạy cùng hệ thống.  
- **Quản lý tường lửa:** Tự động tạo hoặc cập nhật các quy tắc Firewall để cho phép kết nối FTP.  
- **Giao diện cấu hình thân thiện:** Hỗ trợ quản lý mọi thiết lập mà không cần dòng lệnh.

---

## 💾 Cài đặt

Để cài đặt **mFTP Server**, hãy làm theo các bước sau:

1. **Tải xuống:**  
   👉 [Tải mFTP Setup.exe](https://github.com/caophuocdanh/mFTP-Server/releases/download/v1.0/mFTP.Setup.exe)

2. **Chạy trình cài đặt:**  
   Chạy tệp `mFTP Setup.exe` bằng quyền **Administrator**.  
   - Trình cài đặt sẽ hướng dẫn qua từng bước cài đặt.  
   - Tự động tạo thư mục, sao chép tệp, thiết lập tác vụ khởi động cùng Windows.  
   - Tự động thêm quy tắc tường lửa cần thiết.

3. **Hoàn tất:**  
   Sau khi cài đặt, **mFTP Server** sẽ tự động khởi động và chạy ngầm.

---

## 🗑️ Gỡ bỏ

1. Chạy lại tệp `mFTP Setup.exe` bằng quyền Administrator.  
2. Chọn **Gỡ cài đặt (Uninstall)**.  
3. Trình cài đặt sẽ tự động:  
   - Dừng dịch vụ,  
   - Xóa tác vụ lên lịch,  
   - Gỡ cấu hình và tệp cài đặt.

---

## 🚀 Sử dụng

Sau khi cài đặt, **mFTP Server** sẽ chạy ngầm trong khay hệ thống.

1. **Mở cấu hình:**  
   Nhấp chuột phải vào biểu tượng **mFTP** trong khay hệ thống → chọn **Show Config**.  
2. **Cấu hình máy chủ:**  
   - **IP Address:** Tự động phát hiện IP cục bộ.  
   - **Port:** Mặc định `2121`.  
   - **Username:** `scan`  
   - **Password:** `123`  
   - **Directory:** `C:\SCAN`  
3. **Khởi động / Dừng máy chủ:**  
   Nhấn **Start Server** hoặc **Stop Server**.  
4. **Ẩn cửa sổ:**  
   Nhấn **X** để ẩn vào khay hệ thống.  
5. **Thoát ứng dụng:**  
   Chuột phải biểu tượng → **Quit** để thoát hoàn toàn.

---

## 🧾 Thông tin phiên bản

**Version:** `1.0`  
**Build:** `2110`  
**© 2025 mFTP Project**

---

