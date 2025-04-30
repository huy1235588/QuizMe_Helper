import json
import os
from pathlib import Path


def load_json_file(file_path):
    """Đọc dữ liệu từ tệp JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Lỗi khi đọc tệp {file_path}: {e}")
        return None


def save_json_file(data, file_path):
    """Lưu dữ liệu vào tệp JSON."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"Dữ liệu đã được lưu thành công vào {file_path}")
        return True
    except Exception as e:
        print(f"Lỗi khi ghi tệp {file_path}: {e}")
        return False


def process_image(source_dir, original_image_name, new_image_name):
    """Xử lý và đổi tên tệp hình ảnh."""
    if not original_image_name:
        return False

    print(f"Đang tìm kiếm hình ảnh: {original_image_name}")
    
    # Chuyển đổi thành đối tượng Path để xử lý đường dẫn tốt hơn
    source_dir = Path(source_dir)
    
    # Tìm kiếm tệp hình ảnh
    for file_path in source_dir.glob("*"):
        file_name = file_path.name
        if (file_name.lower() == original_image_name.lower() or 
            original_image_name in file_name):
            try:
                # Sử dụng rename thay vì copy để tránh tạo tệp trùng lặp
                file_path.rename(source_dir / new_image_name)
                return True
            except Exception as e:
                print(f"Lỗi khi đổi tên hình ảnh: {e}")
                return False
    
    print(f"Không tìm thấy hình ảnh: {original_image_name}")
    return False


def create_question(slide, question_id, quiz_id, image_url):
    """Tạo đối tượng câu hỏi từ dữ liệu slide."""
    options = []
    
    for j, answer in enumerate(slide.get("answers", []), 1):
        option = {
            "id": (question_id - 1) * 4 + j,
            "question_id": question_id,
            "content": answer.get("text", ""),
            "is_correct": answer.get("isCorrect", False),
        }
        options.append(option)

    return {
        "id": question_id,
        "quiz_id": quiz_id,
        "content": slide.get("question", ""),
        "image_url": image_url,
        "audio_url": None,
        "time_limit": 10,  # Giá trị mặc định
        "points": 1000,    # Giá trị mặc định
        "order_number": question_id,
        "type": "QUIZ",
        "options": options,
    }


def convert_format_json():
    """Chuyển đổi dữ liệu guess flag sang định dạng geography."""
    # Định nghĩa đường dẫn
    data_dir = Path("data")
    input_path = data_dir / "json" / "input.json"
    output_path = data_dir / "json" / "converted_format.json"
    source_image_dir = data_dir / "image" / "3_science & nature" / "1_Animals"

    # Đọc dữ liệu đầu vào
    input_data = load_json_file(input_path)
    if not input_data:
        return

    # Tạo cấu trúc dữ liệu đầu ra
    quiz_id = 1
    questions = []

    # Xử lý các slide
    for i, slide in enumerate(input_data.get("slides", []), 1):
        # Lấy tên hình ảnh gốc
        original_image_name = None
        if slide.get("media") and slide.get("media").get("source"):
            original_image_name = slide.get("media").get("source").split("/")[-1]

        # Đặt tên tệp hình ảnh mới
        new_image_filename = f"quiz_{quiz_id}_question_{i}_1745400000.jpg"
        image_url = f"question_images/{new_image_filename}"

        # Xử lý hình ảnh
        process_image(source_image_dir, original_image_name, new_image_filename)
        
        # Tạo đối tượng câu hỏi
        question = create_question(slide, i, quiz_id, image_url)
        questions.append(question)

    # Tạo đối tượng quiz
    quiz = {
        "id": quiz_id,
        "title": input_data.get("name", ""),
        "description": input_data.get("description", ""),
        "quiz_thumbnails": f"quiz_thumbnails/quiz_thumbnail_{quiz_id}_1745400000.jpg",
        "category_id": 1,
        "creator_id": 1,
        "difficulty": "MEDIUM",
        "is_public": input_data.get("visibility") == "public",
        "play_count": input_data.get("playCount", 0),
        "question_count": len(questions),
        "questions": questions,
    }

    # Lưu kết quả
    geography_format = {"quizzes": [quiz]}
    save_json_file(geography_format, output_path)


if __name__ == "__main__":
    convert_format_json()
