import json
import re


def parse_chemistry_questions(file_path):
    """
    Phân tích các câu hỏi hóa học từ tệp txt và trích xuất dữ liệu câu hỏi
    Xử lý format: A, B cùng dòng; C, D cùng dòng; hoặc A, B, C, D cùng dòng
    """
    questions = []

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Tách theo mẫu câu hỏi (Câu theo sau là số)
    question_blocks = re.split(r"Câu \d+:", content)[
        1:
    ]  # Bỏ qua phần tử trống đầu tiên

    for i, block in enumerate(question_blocks, 1):
        lines = block.strip().split("\n")
        if not lines:
            continue

        # Trích xuất nội dung câu hỏi (dòng đầu tiên)
        question_content = lines[0].strip()

        # Trích xuất các lựa chọn
        options = []
        correct_answer = None

        # Xử lý tất cả các dòng có chứa lựa chọn
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Kiểm tra xem dòng này có chứa các lựa chọn A, B, C, D không
            if re.search(r"[A-D]\.", line):
                # Pattern cải tiến để tìm tất cả lựa chọn trong một dòng
                # Sửa lại pattern để tránh cắt nội dung khi có ký tự A-D
                option_pattern = (
                    r"([A-D])\.\s*([^A-D]*?(?:[A-D][^.]*?)*)(?=\s+[A-D]\.|$)"
                )

                # Hoặc sử dụng pattern đơn giản hơn:
                option_pattern = r"([A-D])\.\s*(.*?)(?=\s+[A-D]\.|$)"

                option_matches = re.finditer(option_pattern, line)

                temp_options = []
                for match in option_matches:
                    option_letter = match.group(1)
                    option_text = match.group(2).strip()

                    # Loại bỏ các ký tự không cần thiết ở cuối và xử lý <CORRECT>
                    option_text = re.sub(r"[;,\s]+$", "", option_text)

                    # Xử lý trường hợp <CORRECT> nằm ở đầu
                    is_correct = "<CORRECT>" in option_text
                    option_text = option_text.replace("<CORRECT>", "").strip()

                    if option_text:  # Chỉ xử lý nếu có text
                        temp_options.append(
                            {
                                "letter": option_letter,
                                "content": option_text,
                                "is_correct": is_correct,
                            }
                        )

                        if is_correct:
                            correct_answer = option_text

                # Thêm tất cả options tìm được
                if temp_options:
                    options.extend(temp_options)

        # Nếu không đủ 4 options với regex, thử phương pháp từng dòng riêng biệt
        if len(options) < 4:
            options.clear()  # Reset để thử lại
            correct_answer = None

            for line in lines[1:]:
                line = line.strip()
                if line and re.match(r"^[A-D]\.", line):
                    # Kiểm tra xem đây có phải là câu trả lời đúng không
                    is_correct = "<CORRECT>" in line
                    # Lấy chữ cái lựa chọn
                    option_letter = line[0]
                    # Làm sạch văn bản lựa chọn
                    option_text = re.sub(r"^[A-D]\.\s*", "", line)
                    option_text = option_text.replace("<CORRECT>", "").strip()

                    if option_text:  # Chỉ thêm nếu có nội dung
                        options.append(
                            {
                                "letter": option_letter,
                                "content": option_text,
                                "is_correct": is_correct,
                            }
                        )

                        if is_correct:
                            correct_answer = option_text

        # Sắp xếp lại các lựa chọn theo thứ tự A, B, C, D
        options.sort(key=lambda x: x.get("letter", "Z"))

        # Kiểm tra tính hợp lệ của câu hỏi
        if len(options) == 4:
            # Kiểm tra xem có đúng 1 đáp án đúng không
            correct_count = sum(1 for opt in options if opt["is_correct"])
            if correct_count == 1:
                questions.append(
                    {
                        "question_number": i,
                        "content": question_content,
                        "options": options,
                        "correct_answer": correct_answer,
                    }
                )
            else:
                print(
                    f"⚠️ Câu {i} có {correct_count} đáp án đúng (phải có đúng 1), bỏ qua..."
                )
        else:
            print(
                f"⚠️ Câu {i} không đủ 4 lựa chọn (có {len(options)} lựa chọn), bỏ qua..."
            )

    return questions


def display_questions(questions):
    """
    Hiển thị danh sách câu hỏi để người dùng chọn
    """
    print("\n" + "=" * 100)
    print("DANH SÁCH CÁC CÂU HỎI HIỆN CÓ:")
    print("=" * 100)

    for i, q in enumerate(questions):
        print(f"\n[{i+1}] Câu {q['question_number']}: {q['content']}")

        # Hiển thị các lựa chọn
        for j, option in enumerate(q["options"]):
            letter = chr(65 + j)  # A, B, C, D
            marker = "✓" if option["is_correct"] else " "
            print(f"    {letter}. {option['content']} {marker}")

        print(f"    → Đáp án đúng: {q['correct_answer']}")
        print("-" * 80)


def display_questions_compact(questions, start_idx=0, count=5):
    """
    Hiển thị câu hỏi dạng compact (ít câu hơn)
    """
    end_idx = min(start_idx + count, len(questions))

    print(f"\nHiển thị câu hỏi {start_idx + 1} đến {end_idx}:")
    print("=" * 80)

    for i in range(start_idx, end_idx):
        q = questions[i]
        print(f"\n[{i+1}] {q['content'][:70]}...")
        print(f"    Đáp án: {q['correct_answer'][:50]}...")

    print(f"\nTổng cộng: {len(questions)} câu hỏi")
    return end_idx


def browse_questions(questions):
    """
    Duyệt câu hỏi theo trang
    """
    current_idx = 0
    questions_per_page = 5

    while True:
        end_idx = display_questions_compact(questions, current_idx, questions_per_page)

        print(f"\nTùy chọn:")
        if current_idx > 0:
            print("p - Trang trước")
        if end_idx < len(questions):
            print("n - Trang tiếp")
        print("a - Xem tất cả")
        print("q - Quay lại menu")

        choice = input("\nChọn: ").lower().strip()

        if choice == "p" and current_idx > 0:
            current_idx = max(0, current_idx - questions_per_page)
        elif choice == "n" and end_idx < len(questions):
            current_idx = end_idx
        elif choice == "a":
            display_questions(questions)
            input("\nNhấn Enter để tiếp tục...")
            break
        elif choice == "q":
            break
        else:
            print("Lựa chọn không hợp lệ!")


def parse_selection(user_input, max_value):
    """
    Phân tích chuỗi lựa chọn của người dùng
    """
    selected = set()

    # Tách theo dấu phẩy
    parts = user_input.split(",")

    for part in parts:
        part = part.strip()

        if "-" in part:
            # Xử lý khoảng (VD: 1-5)
            try:
                start, end = part.split("-")
                start, end = int(start.strip()), int(end.strip())

                if start < 1 or end > max_value or start > end:
                    raise ValueError(f"Khoảng {start}-{end} không hợp lệ!")

                selected.update(range(start, end + 1))
            except ValueError as e:
                raise ValueError(f"Định dạng khoảng không hợp lệ: {part}")

        else:
            # Xử lý số đơn lẻ
            try:
                num = int(part)
                if num < 1 or num > max_value:
                    raise ValueError(f"Số {num} nằm ngoài khoảng 1-{max_value}!")
                selected.add(num)
            except ValueError:
                raise ValueError(f"'{part}' không phải là số hợp lệ!")

    return sorted(list(selected))


def create_quiz_json(selected_questions, quiz_info):
    """
    Tạo cấu trúc JSON cho bài kiểm tra dựa trên định dạng đã cung cấp
    """
    # Tạo ID cơ sở
    quiz_id = quiz_info["id"]
    base_question_id = 100
    base_option_id = 400

    quiz_questions = []

    for i, q in enumerate(selected_questions):
        question_id = base_question_id + i

        # Tạo các lựa chọn với ID thích hợp
        options = []
        for j, option in enumerate(q["options"]):
            option_id = base_option_id + (i * 4) + j
            options.append(
                {
                    "id": option_id,
                    "question_id": question_id,
                    "content": option["content"],
                    "is_correct": option["is_correct"],
                }
            )

        quiz_questions.append(
            {
                "id": question_id,
                "quiz_id": quiz_id,
                "content": q["content"],
                "image_url": None,
                "audio_url": None,
                "time_limit": 15,  # Câu hỏi hóa học có thể cần nhiều thời gian hơn
                "points": 1000,
                "order_number": i + 1,
                "type": "QUIZ",
                "options": options,
            }
        )

    quiz_data = {
        "quizzes": [
            {
                "id": quiz_id,
                "title": quiz_info["title"],
                "description": quiz_info["description"],
                "quiz_thumbnails": quiz_info["thumbnail"],
                "category_id": quiz_info["category_id"],
                "creator_id": 1,
                "difficulty": quiz_info["difficulty"],
                "is_public": True,
                "play_count": 0,
                "question_count": len(selected_questions),
                "favorite_count": 0,
                "questions": quiz_questions,
            }
        ]
    }

    return quiz_data


def create_single_quiz(all_questions):
    """
    Tạo một bài kiểm tra với câu hỏi do người dùng chọn
    """
    print("\n" + "=" * 50)
    print("TẠO BÀI KIỂM TRA MỚI")
    print("=" * 50)

    # Nhập thông tin bài kiểm tra
    quiz_id = int(input("Nhập ID cho bài kiểm tra: "))
    title = input("Nhập tiêu đề bài kiểm tra: ")
    description = input("Nhập mô tả bài kiểm tra: ")

    print("\nChọn độ khó:")
    print("1. EASY")
    print("2. MEDIUM")
    print("3. HARD")
    difficulty_choice = input("Nhập lựa chọn (1-3): ")
    difficulty_map = {"1": "EASY", "2": "MEDIUM", "3": "HARD"}
    difficulty = difficulty_map.get(difficulty_choice, "MEDIUM")

    # Hiển thị câu hỏi và cho phép chọn
    display_questions(all_questions)
    selected_indices = get_user_selection(len(all_questions))

    # Lấy câu hỏi đã chọn
    selected_questions = [all_questions[i - 1] for i in selected_indices]

    # Cấu hình bài kiểm tra
    quiz_config = {
        "id": quiz_id,
        "title": title,
        "description": description,
        "thumbnail": f"quiz_thumbnail_{quiz_id}_{1745400000}.jpg",
        "category_id": 3,
        "difficulty": difficulty,
    }

    # Tạo JSON
    quiz_json = create_quiz_json(selected_questions, quiz_config)

    # Lưu file
    output_file = f"json/chemistry_quiz_{quiz_id}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(quiz_json, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Đã tạo file {output_file} với {len(selected_questions)} câu hỏi")

    # Hiển thị tóm tắt
    print(f"\nTóm tắt bài kiểm tra '{title}':")
    print(f"- ID: {quiz_id}")
    print(f"- Độ khó: {difficulty}")
    print(f"- Số câu hỏi: {len(selected_questions)}")
    print(f"- Câu hỏi đã chọn: {', '.join(map(str, selected_indices))}")


def get_user_selection(max_value):
    """
    Lấy lựa chọn câu hỏi từ người dùng
    """
    while True:
        print(f"\nChọn câu hỏi (1-{max_value}):")
        print("- Có thể chọn nhiều câu: 1,3,5 hoặc 1-5 hoặc 1-3,7,9-12")
        print("- Nhập 'all' để chọn tất cả")

        user_input = input("Nhập lựa chọn: ").strip()

        if user_input.lower() == "all":
            return list(range(1, max_value + 1))

        try:
            selected = parse_selection(user_input, max_value)
            if not selected:
                print("❌ Bạn chưa chọn câu hỏi nào!")
                continue

            print(
                f"✅ Đã chọn {len(selected)} câu hỏi: {', '.join(map(str, selected))}"
            )
            return selected

        except ValueError as e:
            print(f"❌ Lỗi: {e}")
            print("Vui lòng thử lại!")


def main():
    # Phân tích tất cả câu hỏi từ tệp hóa học
    input_file = r"raw-data/hoá học.txt"

    try:
        all_questions = parse_chemistry_questions(input_file)
        print(f"✅ Đã phân tích {len(all_questions)} câu hỏi từ file txt")
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {input_file}")
        print("Vui lòng kiểm tra đường dẫn file!")
        return
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return

    if len(all_questions) == 0:
        print("❌ Không tìm thấy câu hỏi nào trong file!")
        return

    while True:
        print("\n" + "=" * 50)
        print("MENU CHÍNH - QUIZME HELPER")
        print("=" * 50)
        print("1. Duyệt câu hỏi (theo trang)")
        print("2. Xem tất cả câu hỏi")
        print("3. Tạo bài kiểm tra mới")
        print("4. Tạo nhiều bài kiểm tra (batch)")
        print("5. Thoát")

        choice = input("\nChọn chức năng (1-5): ").strip()

        if choice == "1":
            browse_questions(all_questions)

        elif choice == "2":
            display_questions(all_questions)
            input("\nNhấn Enter để tiếp tục...")

        elif choice == "3":
            create_single_quiz(all_questions)
            input("\nNhấn Enter để tiếp tục...")

        elif choice == "4":
            create_multiple_quizzes(all_questions)
            input("\nNhấn Enter để tiếp tục...")

        elif choice == "5":
            print("Tạm biệt!")
            break

        else:
            print("Lựa chọn không hợp lệ!")


def create_multiple_quizzes(all_questions):
    """
    Tạo nhiều bài kiểm tra cùng lúc
    """
    print("\n" + "=" * 50)
    print("TẠO NHIỀU BÀI KIỂM TRA")
    print("=" * 50)

    num_quizzes = int(input("Nhập số lượng bài kiểm tra muốn tạo: "))

    for i in range(num_quizzes):
        print(f"\n--- Tạo bài kiểm tra {i+1}/{num_quizzes} ---")
        create_single_quiz(all_questions)


if __name__ == "__main__":
    main()
