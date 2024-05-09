import os
import sys
import face_recognition

def read_images_and_labels(data_folder):
    images = []
    labels = []

    for filename in os.listdir(data_folder):
        path = os.path.join(data_folder, filename)
        label = os.path.splitext(filename)[0]  # Sử dụng os.path.splitext để lấy nhãn mà không có phần mở rộng

        # Tải ảnh sử dụng thư viện face_recognition
        image = face_recognition.load_image_file(path)

        if image is not None:
            images.append(image)
            labels.append(label)

    return images, labels

def compare_image_with_folder(folder, image_path, progress_callback=None):
    # Tải ảnh mục tiêu
    target_image = face_recognition.load_image_file(image_path)
    target_encoding = face_recognition.face_encodings(target_image)

    if not target_encoding:
        return "Không tìm thấy khuôn mặt trong ảnh mục tiêu."

    target_encoding = target_encoding[0]

    # Đọc ảnh và nhãn từ thư mục dữ liệu huấn luyện
    images, labels = read_images_and_labels(folder)

    # Khởi tạo danh sách để lưu trữ phần trăm tương đồng
    similarity_percentages = []

    # So sánh ảnh mục tiêu với mỗi ảnh trong thư mục
    for i, img in enumerate(images):
        try:
            face_encoding = face_recognition.face_encodings(img)

            if not face_encoding:
                continue  # Bỏ qua ảnh không có khuôn mặt được phát hiện

            face_encoding = face_encoding[0]
            face_distance = face_recognition.face_distance([target_encoding], face_encoding)[0]
            similarity_percentage = (1 - face_distance) * 100
            similarity_percentages.append(similarity_percentage)

            # Gọi hàm callback tiến trình để cập nhật tiến trình
            if progress_callback:
                progress_percentage = (i + 1) / len(images) * 100
                progress_text = f"Tiến độ: {progress_percentage:.2f}%"

                sys.stdout.write(f"\r{progress_text}")
                sys.stdout.flush()

                progress_callback(progress_text)

        except IndexError:
            print("Không tìm thấy khuôn mặt trong một ảnh.")

    # Tính toán phần trăm tương đồng trung bình
    average_similarity = sum(similarity_percentages) / len(similarity_percentages) if similarity_percentages else 0

    # Kiểm tra xem phần trăm tương đồng trung bình có lớn hơn 70% không
    if average_similarity > 70:
        result = f"Chính xác: Độ tương đồng trung bình: {average_similarity:.2f}%"
    else:
        result = f"Sai: Độ tương đồng trung bình: {average_similarity:.2f}%"

    return result
