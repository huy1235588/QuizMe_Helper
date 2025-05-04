import json
import os
import re
import glob


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


def find_max_ids_in_file(file_path):
    """
    Tìm ID lớn nhất của câu hỏi và lựa chọn trong file JSON
    
    Args:
        file_path (str): Đường dẫn đến file JSON
        
    Returns:
        tuple: (max_question_id, max_option_id) trong file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)
        
        max_question_id = 0
        max_option_id = 0
        
        for quiz in quiz_data.get("quizzes", []):
            for question in quiz.get("questions", []):
                question_id = int(question.get("id", 0))
                max_question_id = max(max_question_id, question_id)
                
                for option in question.get("options", []):
                    option_id = int(option.get("id", 0))
                    max_option_id = max(max_option_id, option_id)
        
        return max_question_id, max_option_id
    
    except Exception as e:
        print(f"Lỗi khi đọc file {file_path}: {e}")
        return 0, 0


def find_max_ids_in_directory(directory):
    """
    Tìm ID lớn nhất của câu hỏi và lựa chọn trong tất cả các file JSON trong thư mục
    
    Args:
        directory (str): Đường dẫn đến thư mục chứa các file JSON
        
    Returns:
        tuple: (max_question_id, max_option_id) trong tất cả các file
    """
    max_question_id = 0
    max_option_id = 0
    
    if not os.path.exists(directory):
        return max_question_id, max_option_id
    
    # Tìm tất cả file JSON trong thư mục
    json_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    
    for file_name in json_files:
        file_path = os.path.join(directory, file_name)
        q_id, o_id = find_max_ids_in_file(file_path)
        max_question_id = max(max_question_id, q_id)
        max_option_id = max(max_option_id, o_id)
    
    return max_question_id, max_option_id


def find_max_ids_in_processed_dirs(base_dir="data/json/quiz", excluded_dirs=None):
    """
    Tìm ID lớn nhất từ các thư mục đã xử lý và các file gộp
    
    Args:
        base_dir (str): Thư mục gốc chứa các thư mục quiz
        excluded_dirs (list): Danh sách các thư mục bị loại trừ (sẽ không tìm ID trong các thư mục này)
        
    Returns:
        tuple: (max_question_id, max_option_id) từ tất cả thư mục và file
    """
    if excluded_dirs is None:
        excluded_dirs = []
    
    max_question_id = 0
    max_option_id = 0
    
    # Lấy danh sách tất cả thư mục quiz
    all_quiz_dirs = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and not item.startswith("backup"):
            # Bỏ qua các thư mục trong danh sách loại trừ
            if item not in excluded_dirs:
                all_quiz_dirs.append(item_path)
    
    # Sắp xếp thư mục theo thứ tự bảng chữ cái
    all_quiz_dirs.sort()
    
    print("\nĐang tìm ID lớn nhất từ các thư mục đã xử lý:")
    for quiz_dir in all_quiz_dirs:
        q_id, o_id = find_max_ids_in_directory(quiz_dir)
        if q_id > 0 or o_id > 0:
            print(f"- {os.path.basename(quiz_dir)}: max_question_id={q_id}, max_option_id={o_id}")
            max_question_id = max(max_question_id, q_id)
            max_option_id = max(max_option_id, o_id)
    
    # Tìm trong các file gộp
    merged_files = glob.glob(os.path.join(base_dir, "merged_*_quizzes.json"))
    for file_path in merged_files:
        q_id, o_id = find_max_ids_in_file(file_path)
        if q_id > 0 or o_id > 0:
            print(f"- File {os.path.basename(file_path)}: max_question_id={q_id}, max_option_id={o_id}")
            max_question_id = max(max_question_id, q_id)
            max_option_id = max(max_option_id, o_id)
    
    return max_question_id, max_option_id


def get_directory_number(directory_name):
    """Lấy số từ tên thư mục dạng X_name"""
    match = re.match(r'^(\d+)_', os.path.basename(directory_name))
    return int(match.group(1)) if match else float('inf')


# Thêm hàm mới để tìm ID lớn nhất từ thư mục đã xử lý trước đó
def find_max_ids_in_previous_directory(current_dir_number, quiz_folders):
    """
    Tìm ID lớn nhất từ thư mục đã xử lý liền trước theo thứ tự số thư mục
    
    Args:
        current_dir_number (int): Số thứ tự của thư mục đang xử lý
        quiz_folders (list): Danh sách các thư mục quiz đã sắp xếp theo thứ tự số
        
    Returns:
        tuple: (max_question_id, max_option_id) từ thư mục liền trước
    """
    # Sắp xếp thư mục theo số
    sorted_folders = sorted(quiz_folders, key=get_directory_number)
    
    # Tìm vị trí của thư mục hiện tại
    current_index = -1
    for i, folder in enumerate(sorted_folders):
        folder_number = get_directory_number(folder)
        if folder_number == current_dir_number:
            current_index = i
            break
    
    # Nếu không phải thư mục đầu tiên, tìm ID từ thư mục liền trước
    if current_index > 0:
        previous_dir = sorted_folders[current_index - 1]
        print(f"\nTìm ID từ thư mục liền trước: {os.path.basename(previous_dir)}")
        
        # Tìm ID trong thư mục
        q_id, o_id = find_max_ids_in_directory(previous_dir)
        
        # Nếu không có file trong thư mục, tìm trong file merged của thư mục đó
        if q_id == 0 and o_id == 0:
            base_dir = os.path.dirname(previous_dir)
            folder_name = os.path.basename(previous_dir)
            merged_file = os.path.join(base_dir, f"merged_{folder_name}_quizzes.json")
            if os.path.exists(merged_file):
                q_id, o_id = find_max_ids_in_file(merged_file)
                print(f"- File {os.path.basename(merged_file)}: max_question_id={q_id}, max_option_id={o_id}")
        else:
            print(f"- {os.path.basename(previous_dir)}: max_question_id={q_id}, max_option_id={o_id}")
            
        return q_id, o_id
    
    # Nếu là thư mục đầu tiên, trả về (0, 0)
    return 0, 0


if __name__ == "__main__":
    # Thư mục gốc chứa các thư mục quiz
    base_directory = os.path.join("data", "json", "quiz")
    
    # Lấy danh sách các thư mục con (1_geography, 4_science_nature, ...)
    quiz_folders = []
    for item in os.listdir(base_directory):
        item_path = os.path.join(base_directory, item)
        if os.path.isdir(item_path) and re.match(r'^\d+_', item) and not item.startswith("backup"):
            quiz_folders.append(item_path)
    
    # Sắp xếp thư mục theo số (1_geography trước 4_science_nature)
    quiz_folders.sort(key=get_directory_number)
    
    if not quiz_folders:
        print("Không tìm thấy thư mục quiz nào để xử lý.")
        exit()
    
    try:
        for i, directory_path in enumerate(quiz_folders):
            folder_name = os.path.basename(directory_path)
            print(f"\n{'='*50}")
            print(f"Đang xử lý thư mục {i+1}/{len(quiz_folders)}: {folder_name}")
            print(f"{'='*50}")
            
            # Lấy tất cả file JSON trong thư mục
            json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]
            
            # Sắp xếp file theo thứ tự bảng chữ cái
            json_files.sort()
            
            if not json_files:
                print(f"Không có file JSON nào trong thư mục {folder_name}")
                continue
                
            # Thư mục đầu tiên (1_geography) hoặc thư mục chỉ định nhập thủ công
            if i == 0 or folder_name == "1_geography":
                # Yêu cầu ID ban đầu cho file đầu tiên
                question_id = int(input("Nhập ID bắt đầu cho câu hỏi của file đầu tiên: "))
                option_id = int(input("Nhập ID bắt đầu cho lựa chọn của file đầu tiên: "))
            else:
                # Lấy số thứ tự của thư mục hiện tại
                current_dir_number = get_directory_number(directory_path)
                
                # Tìm ID lớn nhất từ thư mục liền trước theo thứ tự số
                max_question_id, max_option_id = find_max_ids_in_previous_directory(current_dir_number, quiz_folders)
                
                question_id = max_question_id + 1
                option_id = max_option_id + 1
                print(f"ID cao nhất từ thư mục xử lý trước đó: question_id={max_question_id}, option_id={max_option_id}")
                print(f"Tự động sử dụng ID bắt đầu: question_id={question_id}, option_id={option_id}")
            
            print(f"\nĐã tìm thấy {len(json_files)} file JSON để xử lý.")
            
            # Xử lý từng file theo thứ tự
            for j, file_name in enumerate(json_files):
                file_path = os.path.join(directory_path, file_name)
                print(f"\nĐang xử lý file {j+1}/{len(json_files)}: {file_name}")
                print(f"Sử dụng ID câu hỏi bắt đầu: {question_id}, ID lựa chọn: {option_id}")
                
                # Điều chỉnh ID và lấy ID lớn nhất
                max_question_id, max_option_id = adjust_quiz_ids(
                    file_path, question_id, option_id
                )
                
                # Đặt ID bắt đầu cho file tiếp theo
                question_id = max_question_id + 1
                option_id = max_option_id + 1
                
                if j < len(json_files) - 1:
                    print(f"File tiếp theo sẽ bắt đầu với ID câu hỏi: {question_id}, ID lựa chọn: {option_id}")
            
            # Gộp các file trong thư mục hiện tại
            output_file = os.path.join(base_directory, f"merged_{folder_name}_quizzes.json")
            merged_file = merge_quiz_jsons(directory_path, output_file)
            if merged_file:
                print(f"Đã hoàn tất quá trình gộp file thư mục {folder_name}.")
            else:
                print(f"Gộp file thư mục {folder_name} không thành công.")
        
        print("\nĐã xử lý tất cả các thư mục quiz thành công!")
        
    except ValueError:
        print("Vui lòng nhập giá trị số nguyên hợp lệ cho ID.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
