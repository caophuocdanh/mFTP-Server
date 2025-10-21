# mFTP Server
![mFTP](app.png)
## Giới thiệu

mFTP Server là một ứng dụng máy chủ FTP đơn giản và nhẹ, được thiết kế để dễ dàng chia sẻ tệp tin trên mạng cục bộ của bạn. Ứng dụng này chạy ngầm trong khay hệ thống và cung cấp giao diện cấu hình thân thiện.

## Chức năng chính

-   **Máy chủ FTP đơn giản:** Cho phép bạn thiết lập một máy chủ FTP với tên người dùng, mật khẩu và thư mục chia sẻ tùy chỉnh.
-   **Chạy ngầm:** Ứng dụng chạy trong khay hệ thống, không làm phiền không gian làm việc của bạn.
-   **Tự động khởi động:** Có thể cấu hình để tự động khởi động cùng hệ thống.
-   **Quản lý tường lửa:** Tự động tạo hoặc cập nhật các quy tắc tường lửa để cho phép kết nối FTP.
-   **Giao diện cấu hình:** Giao diện người dùng đồ họa (GUI) đơn giản để cấu hình máy chủ.

## Cài đặt

Để cài đặt mFTP Server, hãy làm theo các bước sau:

1.  **Tải xuống:** Tải xuống tệp `mFTP Server Setup.exe` từ [https://github.com/caophuocdanh/mFTP-Server/releases/download/v1.0/mFTP.Setup.exe].
2.  **Chạy trình cài đặt:** Chạy tệp `mFTP Server Setup.exe` với quyền quản trị.
    *   Trình cài đặt sẽ hướng dẫn bạn qua quá trình cài đặt.
    *   Nó sẽ tạo các thư mục cần thiết, sao chép tệp ứng dụng và thiết lập tác vụ lên lịch để ứng dụng tự động khởi động khi đăng nhập.
    *   Nó cũng sẽ cố gắng tạo các quy tắc tường lửa cần thiết.
3.  **Hoàn tất:** Sau khi cài đặt hoàn tất, máy chủ FTP sẽ tự động khởi động và chạy ngầm.

## Gỡ bỏ

Để gỡ bỏ mFTP Server, hãy làm theo các bước sau:

1.  **Chạy trình cài đặt:** Chạy tệp `mFTP Server Setup.exe` với quyền quản trị.
2.  **Chọn Gỡ cài đặt:** Trong menu trình cài đặt, chọn tùy chọn "Gỡ cài đặt".
3.  **Hoàn tất:** Trình cài đặt sẽ dừng máy chủ, xóa tác vụ lên lịch, xóa tệp cấu hình và gỡ bỏ thư mục cài đặt.

## Sử dụng

Sau khi cài đặt, mFTP Server sẽ chạy ngầm trong khay hệ thống của bạn.

1.  **Mở cấu hình:** Nhấp chuột phải vào biểu tượng mFTP Server trong khay hệ thống và chọn "Show Config" để mở giao diện cấu hình.
2.  **Cấu hình máy chủ:**
    *   **IP Address:** Địa chỉ IP cục bộ của máy tính bạn (thường được tự động phát hiện).
    *   **Port:** Cổng mà máy chủ FTP sẽ lắng nghe (mặc định là 2121). Nếu cổng này đang được sử dụng bởi một ứng dụng khác, máy chủ sẽ không thể khởi động.
    *   **Username:** Tên người dùng để đăng nhập vào máy chủ FTP (mặc định là "scan").
    *   **Password:** Mật khẩu để đăng nhập vào máy chủ FTP (mặc định là "123").
    *   **Directory:** Thư mục mà máy chủ FTP sẽ chia sẻ (mặc định là `C:\SCAN`).
3.  **Khởi động/Dừng máy chủ:** Nhấp vào nút "Start Server" để khởi động máy chủ FTP. Nút này sẽ chuyển thành "Stop Server" khi máy chủ đang chạy.
4.  **Ẩn cửa sổ:** Nhấp vào nút đóng cửa sổ (X) để ẩn cửa sổ cấu hình vào khay hệ thống.
5.  **Thoát ứng dụng:** Nhấp chuột phải vào biểu tượng mFTP Server trong khay hệ thống và chọn "Quit" để dừng máy chủ và thoát ứng dụng.

---

**version 1.0 build 2110 (@) 2025**
