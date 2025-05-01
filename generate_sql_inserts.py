import json
import os


def load_json(file_path):
    """Tải dữ liệu JSON từ file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_inserts(json_data):
    """Tạo các câu lệnh SQL INSERT từ dữ liệu JSON."""
    sql_statements = []

    # Thêm transaction start
    sql_statements.append("START TRANSACTION;")

    # Thêm câu lệnh INSERT cho bảng category
    for category in json_data.get("categories", []):
        category_insert = f"""
INSERT INTO category (id, name, description, icon_url, quiz_count, total_play_count, is_active)
VALUES ({category['id']}, 
        '{category['name'].replace("'", "''")}', 
        '{category['description'].replace("'", "''")}', 
        '{category['icon_url']}', 
        {category['quiz_count']},
        {category['total_play_count']},
        {str(category['is_active']).lower()});
"""
        sql_statements.append(category_insert)

    # Lặp qua từng quiz trong dữ liệu JSON
    for quiz in json_data.get("quizzes", []):
        # Insert quiz
        quiz_insert = f"""
INSERT INTO quiz (id, title, description, quiz_thumbnails, creator_id, difficulty, is_public, play_count, question_count)
VALUES ({quiz['id']}, 
        '{quiz['title'].replace("'", "''")}', 
        '{quiz['description'].replace("'", "''")}', 
        '{quiz['quiz_thumbnails']}', 
        {quiz['creator_id']}, 
        '{quiz['difficulty']}', 
        {str(quiz['is_public']).lower()}, 
        {quiz['play_count']}, 
        {quiz['question_count']});
"""
        sql_statements.append(quiz_insert)

        # Insert quan hệ quiz_category
        quiz_category_insert = f"""
INSERT INTO quiz_category (quiz_id, category_id)
VALUES ({quiz['id']}, {quiz['category_id']});
"""
        sql_statements.append(quiz_category_insert)

        # Xử lý các câu hỏi (questions)
        if "questions" in quiz:
            # Kiểm tra cấu trúc của questions - trong một số trường hợp nó là mảng các câu hỏi
            # trong trường hợp khác nó là mảng các nhóm câu hỏi
            if isinstance(quiz["questions"], list) and all(
                isinstance(item, dict) and "questions" in item
                for item in quiz["questions"]
            ):
                # Cấu trúc nhóm câu hỏi
                for question_group in quiz["questions"]:
                    for question in question_group.get("questions", []):
                        process_question(question, sql_statements)
            else:
                # Cấu trúc mảng đơn giản
                for question in quiz["questions"]:
                    process_question(question, sql_statements)

    # Xử lý autocomplete_hints nếu có
    for hint in json_data.get("autocomplete_hints", []):
        hint_insert = f"""
INSERT INTO autocomplete_hint (id, content, priority)
VALUES ({hint['id']}, 
        '{hint['content'].replace("'", "''")}', 
        {hint['priority']});
"""
        sql_statements.append(hint_insert)

    # Thêm transaction commit
    sql_statements.append("COMMIT;")

    return "\n".join(sql_statements)


def process_question(question, sql_statements):
    """Xử lý từng câu hỏi và tùy chọn của nó."""
    # Xử lý giá trị NULL cho image_url và audio_url
    image_url = f"'{question['image_url']}'" if question.get("image_url") else "NULL"
    audio_url = f"'{question['audio_url']}'" if question.get("audio_url") else "NULL"

    question_insert = f"""
INSERT INTO question (id, quiz_id, content, image_url, audio_url, time_limit, points, order_number, type)
VALUES ({question['id']}, 
        {question['quiz_id']}, 
        '{question['content'].replace("'", "''")}', 
        {image_url}, 
        {audio_url}, 
        {question['time_limit']}, 
        {question['points']}, 
        {question['order_number']}, 
        '{question['type']}');
"""
    sql_statements.append(question_insert)

    # Xử lý các tùy chọn câu trả lời
    for option in question.get("options", []):
        # Xử lý giá trị NULL cho content
        option_content = (
            f"'{option['content'].replace('\'', '\'\'')}'"
            if option.get("content")
            else "NULL"
        )
        option_insert = f"""
INSERT INTO question_option (id, question_id, content, is_correct)
VALUES ({option['id']}, 
        {option['question_id']}, 
        {option_content}, 
        {str(option['is_correct']).lower()});
"""
        sql_statements.append(option_insert)


def save_sql(sql_content, output_path):
    """Lưu nội dung SQL vào file."""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(sql_content)


def main():
    """Hàm chính để xử lý việc tạo các câu lệnh SQL từ các file JSON."""
    # Xác định đường dẫn
    json_directory = os.path.join("data", "json", "category")
    output_directory = os.path.join("data", "sql")

    # Tạo thư mục đầu ra nếu nó không tồn tại
    os.makedirs(output_directory, exist_ok=True)

    # Xử lý tất cả các file JSON trong thư mục
    for filename in os.listdir(json_directory):
        # Kiểm tra file json và khác rỗng
        if filename.endswith('.json') and os.path.getsize(os.path.join(json_directory, filename)) > 0:
            print(f"Đang xử lý {filename}...")
            json_path = os.path.join(json_directory, filename)
            output_name = f"{os.path.splitext(filename)[0]}_inserts.sql"
            output_path = os.path.join(output_directory, output_name)

            print(f"Đang xử lý {json_path}...")
            json_data = load_json(json_path)
            sql_content = generate_inserts(json_data)
            save_sql(sql_content, output_path)
            print(f"Đã lưu SQL inserts vào {output_path}")


if __name__ == "__main__":
    main()
