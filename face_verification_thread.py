from PyQt5.QtCore import QThread, pyqtSignal
from xacminh_face import compare_image_with_folder


class FaceVerificationThread(QThread):
    # Tín hiệu để thông báo về việc cập nhật tiến trình và kết quả
    progress_updated = pyqtSignal(str)
    result_updated = pyqtSignal(str)

    def __init__(self, folder, image_path):
        super(FaceVerificationThread, self).__init__()
        self.folder = folder
        self.image_path = image_path

    def run(self):
        try:
            # Gọi hàm xác minh khuôn mặt từ module xacminh_face
            result = compare_image_with_folder(self.folder, self.image_path, self.update_progress)

            # Gửi kết quả thông báo tới giao diện
            self.result_updated.emit(result)
        except Exception as e:
            # Xử lý lỗi và gửi thông báo lỗi tới giao diện
            error_message = f"Đã xảy ra lỗi: {str(e)}"
            print(error_message)  # In lỗi ra console (có thể ghi log)
            self.result_updated.emit(error_message)

    def update_progress(self, progress_text):
        # Hàm này được gọi từ hàm xác minh để cập nhật tiến trình và gửi tín hiệu tới giao diện
        self.progress_updated.emit(progress_text)
