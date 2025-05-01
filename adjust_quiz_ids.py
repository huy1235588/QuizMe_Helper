import json
import os
import re


def merge_quiz_jsons(directory_path, output_file=None):
    """
    Gộp các file JSON của bài kiểm tra trong một thư mục vào một file duy nhất

    Args:
        directory_path (str): Đường dẫn đến thư mục chứa các file JSON đã xử lý
        output_file (str, optional): Tên file đầu ra. Mặc định là merged_quizzes.json trong thư mục gốc

    Returns:
        str: Đường dẫn đến file đã gộp
    """
    try:
        # Khởi tạo cấu trúc JSON kết quả với mảng quizzes rỗng
        merged_data = {"quizzes": []}

        # Lấy tất cả file JSON trong thư mục
        json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
        json_files.sort()

        print(f"\nĐang gộp {len(json_files)} file JSON...")

        # Đọc từng file và gộp vào merged_data
        for file_name in json_files:
            file_path = os.path.join(directory_path, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                quiz_data = json.load(f)

                if "quizzes" in quiz_data:
                    # Thêm từng quiz vào mảng quizzes của kết quả
                    for quiz in quiz_data["quizzes"]:
                        merged_data["quizzes"].append(quiz)
                    print(f"Đã gộp dữ liệu từ {file_name}")
                else:
                    print(f"Bỏ qua {file_name}: không tìm thấy mảng 'quizzes'")

        # Xác định đường dẫn file đầu ra
        if not output_file:
            output_file = os.path.join(
                os.path.dirname(directory_path), "merged_quizzes.json"
            )

        # Ghi file kết quả
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)

        print(
            f"\nĐã gộp thành công {len(merged_data['quizzes'])} bài kiểm tra vào file: {output_file}"
        )
        return output_file

    except Exception as e:
        print(f"Lỗi khi gộp file: {e}")
        return None


def adjust_quiz_ids(file_path, new_start_question_id, new_start_option_id):
    """
    Điều chỉnh ID của câu hỏi và lựa chọn trong file JSON của bài kiểm tra để bắt đầu từ số được chỉ định
    và cập nhật URL hình ảnh để sử dụng ID câu hỏi thay vì số thứ tự

    Args:
        file_path (str): Đường dẫn đến file JSON bài kiểm tra
        new_start_question_id (int): ID bắt đầu mới cho câu hỏi
        new_start_option_id (int): ID bắt đầu mới cho lựa chọn

    Returns:
        tuple: (max_question_id, max_option_id) sau khi điều chỉnh
    """
    try:
        # Đọc file JSON gốc
        with open(file_path, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        # Tạo thư mục backup nếu chưa tồn tại
        backup_dir = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_dir, exist_ok=True)

        # Tạo bản sao lưu của file gốc trong thư mục backup
        backup_filename = os.path.basename(file_path) + ".backup"
        backup_path = os.path.join(backup_dir, backup_filename)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
        print(f"Backup đã lưu vào {backup_path}")

        max_question_id = new_start_question_id
        max_option_id = new_start_option_id

        # Xử lý từng bài kiểm tra
        for quiz in quiz_data["quizzes"]:
            if "questions" in quiz:
                current_question_id = new_start_question_id
                current_option_id = new_start_option_id

                for question in quiz["questions"]:
                    # Lưu ID gốc để cập nhật các mối quan hệ
                    original_question_id = question["id"]

                    # Cập nhật ID câu hỏi
                    question["id"] = current_question_id
                    max_question_id = max(max_question_id, current_question_id)

                    # Cập nhật mẫu URL hình ảnh để sử dụng ID câu hỏi thay vì số thứ tự
                    if "image_url" in question and question["image_url"]:
                        # Thay thế quiz_x_question_y bằng quiz_x_question_id
                        quiz_id = quiz["id"]
                        pattern = f"quiz_{quiz_id}_question_\\d+"
                        replacement = f"quiz_{quiz_id}_question_{current_question_id}"
                        question["image_url"] = re.sub(
                            pattern, replacement, question["image_url"]
                        )

                    # Cập nhật các lựa chọn
                    if "options" in question:
                        for option in question["options"]:
                            # Cập nhật ID lựa chọn
                            option["id"] = current_option_id
                            max_option_id = max(max_option_id, current_option_id)

                            # Cập nhật tham chiếu question_id trong các lựa chọn
                            option["question_id"] = current_question_id

                            current_option_id += 1

                    current_question_id += 1

        # Lưu file JSON đã cập nhật
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)

        print(f"Đã cập nhật {file_path} với ID mới:")
        print(f"- Câu hỏi bắt đầu từ: {new_start_question_id}")
        print(f"- Lựa chọn bắt đầu từ: {new_start_option_id}")
        print(f"- URL hình ảnh đã cập nhật để sử dụng ID câu hỏi")

        return max_question_id, max_option_id

    except Exception as e:
        print(f"Lỗi: {e}")
        return new_start_question_id - 1, new_start_option_id - 1


if __name__ == "__main__":
    # Thư mục chứa các file JSON
    directory_path = os.path.join("data", "json", "quiz", "7_sports")

    # Lấy tất cả file JSON trong thư mục
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]

    # Sắp xếp file theo thứ tự bảng chữ cái
    json_files.sort()

    try:
        # Yêu cầu ID ban đầu cho file đầu tiên
        question_id = int(input("Nhập ID bắt đầu cho câu hỏi của file đầu tiên: "))
        option_id = int(input("Nhập ID bắt đầu cho lựa chọn của file đầu tiên: "))

        print(f"\nĐã tìm thấy {len(json_files)} file JSON để xử lý.")

        # Xử lý từng file theo thứ tự
        for i, file_name in enumerate(json_files):
            file_path = os.path.join(directory_path, file_name)
            print(f"\nĐang xử lý file {i+1}/{len(json_files)}: {file_name}")
            print(
                f"Sử dụng ID câu hỏi bắt đầu: {question_id}, ID lựa chọn: {option_id}"
            )

            # Điều chỉnh ID và lấy ID lớn nhất
            max_question_id, max_option_id = adjust_quiz_ids(
                file_path, question_id, option_id
            )

            # Đặt ID bắt đầu cho file tiếp theo
            question_id = max_question_id + 1
            option_id = max_option_id + 1

            if i < len(json_files) - 1:
                print(
                    f"File tiếp theo sẽ bắt đầu với ID câu hỏi: {question_id}, ID lựa chọn: {option_id}"
                )

        output_file = os.path.join(directory_path, f"merged_{os.path.basename(directory_path)}_quizzes.json")
        merged_file = merge_quiz_jsons(directory_path, output_file)
        if merged_file:
            print(f"Đã hoàn tất quá trình gộp file.")
        else:
            print("Gộp file không thành công.")

    except ValueError:
        print("Vui lòng nhập giá trị số nguyên hợp lệ cho ID.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
