import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel, QTextEdit, QInputDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from PIL import Image
import threading
import time
from face_verification_thread import FaceVerificationThread  # Giả sử bạn có một module tên là 'face_verification_thread'

class FaceVerificationApp(QDialog):
    def __init__(self):
        super(FaceVerificationApp, self).__init__()

        # Khởi tạo camera và thiết lập timer để cập nhật khung hình
        self.camera = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Cập nhật khung hình mỗi 30 mili giây

        # Các thành phần giao diện
        self.image_label = QLabel(self)
        self.result_text = QTextEdit(self)
        self.capture_button = QPushButton("Chụp ảnh để xác minh", self)
        self.verify_button = QPushButton("Xác minh", self)
        self.traiding_button = QPushButton("Training", self)

        # Thiết lập layout của giao diện
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.verify_button)
        layout.addWidget(self.traiding_button)
        layout.addWidget(self.result_text)

        # Kết nối các nút với các hàm xử lý tương ứng
        self.capture_button.clicked.connect(self.capture_image)
        self.verify_button.clicked.connect(self.verify_face)
        self.traiding_button.clicked.connect(self.start_traiding)

    def update_frame(self):
        # Hàm cập nhật khung hình từ camera
        ret, frame = self.camera.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Chuyển đổi thành đối tượng QImage và hiển thị trên giao diện
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

    def capture_image(self):
        # Hàm chụp ảnh từ camera và lưu lại
        ret, frame = self.camera.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imwrite("xacminh.jpg", frame)

            # Chuyển đổi thành đối tượng Image của Pillow và hiển thị thông báo trên giao diện
            image_pil = Image.fromarray(frame_rgb)
            self.result_text.clear()
            self.result_text.append("Đã chụp và lưu ảnh.")

    def capture_images_async(self, user_name):

        def capture_images():
            captured_images = []
            for i in range(3):
                ret, frame = self.camera.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    captured_images.append(frame_rgb)
                time.sleep(0.05)  # Đợi 50 mili giây giữa mỗi lần chụp

            for i, image in enumerate(captured_images):
                # Tạo thư mục nếu chưa tồn tại
                user_dir = f"training/{user_name}"
                os.makedirs(user_dir, exist_ok=True)

                # Lưu ảnh với tên người dùng
                image_path = f"{user_dir}/captured_image_{i + 1}.jpg"
                cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                self.result_text.append(f"Đã chụp và lưu ảnh cho {user_name}: {i + 1} ảnh.")

        # Tạo một luồng mới để chạy hàm chụp ảnh không đồng bộ
        thread = threading.Thread(target=capture_images)
        thread.start()

    def verify_face(self):
        # Hàm xác minh khuôn mặt
        user_name, ok_pressed = QInputDialog.getText(self, "Xác minh", "Nhập tên người dùng:")
        if ok_pressed and user_name:
            user_dir = f"training/{user_name}"
            if os.path.exists(user_dir) and os.path.isdir(user_dir):
                self.result_text.clear()
                self.result_text.append(f"Xác minh khuôn mặt cho người dùng: {user_name}")

                # Tạo một luồng mới để xác minh khuôn mặt
                self.face_verification_thread = FaceVerificationThread(user_dir, "xacminh.jpg")
                self.face_verification_thread.progress_updated.connect(self.update_result_text)
                self.face_verification_thread.result_updated.connect(self.update_result_text)

                # Khởi động luồng xác minh khuôn mặt
                self.face_verification_thread.start()
            else:
                self.result_text.clear()
                self.result_text.append(f"Yêu cầu thêm người dùng '{user_name}' cho training.")

    def update_result_text(self, text):
        # Hàm cập nhật kết quả trên giao diện
        self.result_text.append(text)

    def start_traiding(self):
        # Hàm bắt đầu traiding
        user_name, ok_pressed = QInputDialog.getText(self, "Training", "Nhập tên người dùng:")
        if ok_pressed and user_name:
            self.result_text.clear()
            self.result_text.append(f"Bắt đầu training cho người dùng: {user_name}")

            # Sử dụng luồng để chụp ảnh không đồng bộ
            self.capture_images_async(user_name)


if __name__ == "__main__":
    # Chạy ứng dụng
    app = QApplication(sys.argv)
    window = FaceVerificationApp()
    window.setWindowTitle("Xác minh khuôn mặt")
    window.show()
    sys.exit(app.exec_())
