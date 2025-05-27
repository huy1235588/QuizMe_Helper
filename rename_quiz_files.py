import os
import re
import time

def rename_quiz_files(folder_path, old_x, new_x, old_z=None, new_z=None, rename_folder=False, same_z_for_all=False, start_y=None):
    """
    Đổi tên các file có dạng quiz_x_question_y_z hoặc quiz_thumbnail_x_z 
    thành quiz_new_x_question_y_z hoặc quiz_thumbnail_new_x_z
    Có thể thay đổi cả phần z nếu cần
    
    Args:
        folder_path: Đường dẫn đến thư mục chứa các file
        old_x: Giá trị x hiện tại cần thay đổi
        new_x: Giá trị x mới
        old_z: Chuỗi z cũ (nếu cần thay đổi)
        new_z: Chuỗi z mới (nếu cần thay đổi)
        rename_folder: Có đổi tên thư mục hay không
        same_z_for_all: Sử dụng cùng một z cho tất cả file
        start_y: Số bắt đầu cho y (nếu None thì giữ nguyên y cũ)
    """
    # Thống kê số lượng file đã đổi tên
    renamed_count = 0
    
    # Nếu có start_y, cần thu thập tất cả file question để sắp xếp
    question_files = []
    
    # Mẫu regex để tìm các file dạng quiz_x_question_y_z
    pattern_question = re.compile(f"quiz_{old_x}_question_(\d+)_(.+)")
    
    # Mẫu regex để tìm các file dạng quiz_thumbnail_x_z
    pattern_thumbnail = re.compile(f"quiz_thumbnail_{old_x}_(.+)")
    
    # Danh sách các thao tác đổi tên cần thực hiện
    rename_operations = []
    
    # Nếu có start_y, thu thập và sắp xếp các file question trước
    if start_y is not None:
        for filename in os.listdir(folder_path):
            match_question = pattern_question.match(filename)
            if match_question:
                old_y = int(match_question.group(1))
                z = match_question.group(2)
                question_files.append((old_y, filename, z))
        
        # Sắp xếp theo y cũ
        question_files.sort(key=lambda x: x[0])
    
    # Thu thập tất cả các thao tác đổi tên trước khi thực hiện
    for filename in os.listdir(folder_path):
        # Kiểm tra file dạng quiz_x_question_y_z
        match_question = pattern_question.match(filename)
        if match_question:
            old_y = int(match_question.group(1))  # Lấy giá trị y cũ
            z = match_question.group(2)  # Lấy phần z
            
            # Quyết định giá trị y mới
            if start_y is not None:
                # Tìm vị trí của file này trong danh sách đã sắp xếp
                for index, (file_old_y, file_name, _) in enumerate(question_files):
                    if file_name == filename:
                        y = start_y + index
                        break
            else:
                y = old_y  # Giữ nguyên y cũ
            
            # Lấy phần mở rộng của file
            _, file_extension = os.path.splitext(z)
            
            # Quyết định giá trị z mới
            if same_z_for_all:
                # Dùng cùng một z cho tất cả file nhưng giữ nguyên phần mở rộng
                z = f"{new_z}{file_extension}"
            elif old_z is not None and new_z is not None and old_z in z:
                # Thay thế z cũ bằng z mới
                z = z.replace(old_z, new_z)
            
            # Tạo tên file mới
            new_filename = f"quiz_{new_x}_question_{y}_{z}"
            
            # Thêm vào danh sách thao tác
            rename_operations.append((filename, new_filename, "question"))
            continue
        
        # Kiểm tra file dạng quiz_thumbnail_x_z
        match_thumbnail = pattern_thumbnail.match(filename)
        if match_thumbnail:
            z = match_thumbnail.group(1)  # Lấy phần z
            
            # Lấy phần mở rộng của file
            _, file_extension = os.path.splitext(z)
            
            # Quyết định giá trị z mới
            if same_z_for_all:
                # Dùng cùng một z cho tất cả file nhưng giữ nguyên phần mở rộng
                z = f"{new_z}{file_extension}"
            elif old_z is not None and new_z is not None and old_z in z:
                # Thay thế z cũ bằng z mới
                z = z.replace(old_z, new_z)
            
            # Tạo tên file mới
            new_filename = f"quiz_thumbnail_{new_x}_{z}"
            
            # Thêm vào danh sách thao tác
            rename_operations.append((filename, new_filename, "thumbnail"))
    
    # Thực hiện đổi tên với tên tạm thời trước để tránh xung đột
    temp_suffix = f"_temp_{int(time.time())}"
    
    # Bước 1: Đổi tất cả file thành tên tạm thời
    temp_renames = []
    for old_filename, new_filename, file_type in rename_operations:
        old_path = os.path.join(folder_path, old_filename)
        temp_filename = old_filename + temp_suffix
        temp_path = os.path.join(folder_path, temp_filename)
        
        try:
            os.rename(old_path, temp_path)
            temp_renames.append((temp_filename, new_filename, file_type))
        except Exception as e:
            print(f"Lỗi khi đổi tên tạm thời {old_filename}: {e}")
    
    # Bước 2: Đổi từ tên tạm thời thành tên cuối cùng
    for temp_filename, new_filename, file_type in temp_renames:
        temp_path = os.path.join(folder_path, temp_filename)
        new_path = os.path.join(folder_path, new_filename)
        
        try:
            os.rename(temp_path, new_path)
            old_filename = temp_filename.replace(temp_suffix, "")
            print(f"Đã đổi tên {file_type}: {old_filename} -> {new_filename}")
            renamed_count += 1
        except Exception as e:
            print(f"Lỗi khi đổi tên cuối cùng {temp_filename}: {e}")
            # Khôi phục tên gốc nếu có lỗi
            old_filename = temp_filename.replace(temp_suffix, "")
            old_path = os.path.join(folder_path, old_filename)
            try:
                os.rename(temp_path, old_path)
                print(f"Đã khôi phục tên gốc: {old_filename}")
            except:
                pass
    
    # Đổi tên thư mục nếu được yêu cầu
    if rename_folder:
        # Lấy tên thư mục cha và tên thư mục hiện tại
        parent_dir = os.path.dirname(folder_path)
        current_folder_name = os.path.basename(folder_path)
        
        # Kiểm tra nếu tên thư mục có dạng số_tên (ví dụ: 1_Animals)
        folder_pattern = re.compile(r"(\d+)_(.+)")
        match_folder = folder_pattern.match(current_folder_name)
        
        if match_folder:
            folder_number = match_folder.group(1)
            folder_name = match_folder.group(2)
            
            # Thay đổi folder_name nếu được chỉ định
            if old_z is not None and new_z is not None and old_z in folder_name:
                folder_name = folder_name.replace(old_z, new_z)
            
            # Tạo tên thư mục mới (thay đổi số)
            new_folder_name = f"{new_x}_{folder_name}"
            new_folder_path = os.path.join(parent_dir, new_folder_name)
            
            # Đổi tên thư mục
            os.rename(folder_path, new_folder_path)
            print(f"Đã đổi tên thư mục: {current_folder_name} -> {new_folder_name}")
            return new_folder_path, renamed_count
    
    return folder_path, renamed_count

def analyze_quiz_files(folder_path, old_x):
    """
    Phân tích các file trong thư mục để giúp người dùng quyết định cách đổi tên
    """
    # Mẫu regex để tìm các file
    pattern_question = re.compile(f"quiz_{old_x}_question_(\d+)_(.+)")
    pattern_thumbnail = re.compile(f"quiz_thumbnail_{old_x}_(.+)")
    
    # Đếm số lượng file và z khác nhau
    question_count = 0
    thumbnail_count = 0
    z_values = set()
    
    # Phân tích các file
    for filename in os.listdir(folder_path):
        match_question = pattern_question.match(filename)
        if match_question:
            z = match_question.group(2)  # Lấy phần z
            z_values.add(z)
            question_count += 1
            continue
            
        match_thumbnail = pattern_thumbnail.match(filename)
        if match_thumbnail:
            z = match_thumbnail.group(1)  # Lấy phần z
            z_values.add(z)
            thumbnail_count += 1
    
    return {
        "question_count": question_count,
        "thumbnail_count": thumbnail_count,
        "total_files": question_count + thumbnail_count,
        "unique_z_count": len(z_values),
        "z_values": list(z_values)[:5]  # Hiển thị tối đa 5 giá trị z đầu tiên
    }

if __name__ == "__main__":
    # Thư mục chứa các file quiz
    folder_path = "data/image/7_sports/56_Guess Soccer Players By Picture"

    # Nhập giá trị x cũ và x mới
    old_x = input("Nhập giá trị x cũ: ") or "56"
    old_x = int(old_x)
    
    new_x = input(f"Nhập giá trị x mới (mặc định: {old_x}): ") or str(old_x)
    new_x = int(new_x)
    
    # Phân tích các file trong thư mục
    analysis = analyze_quiz_files(folder_path, old_x)
    
    print(f"\n=== PHÂN TÍCH FILE QUIZ ===")
    print(f"Tổng số file: {analysis['total_files']}")
    print(f"Số file câu hỏi: {analysis['question_count']}")
    print(f"Số file thumbnail: {analysis['thumbnail_count']}")
    print(f"Số giá trị z khác nhau: {analysis['unique_z_count']}")
    if analysis['z_values']:
        print(f"Một số giá trị z: {', '.join(analysis['z_values'])}")
    
    # Nhập số bắt đầu cho y
    start_y = None
    if analysis['question_count'] > 0:
        start_y_input = input(f"\nĐổi số thứ tự y? Nhập số bắt đầu (Enter để giữ nguyên): ")
        if start_y_input.strip():
            start_y = int(start_y_input)
    
    # Quyết định cách xử lý z
    use_same_z = False
    old_z = None
    new_z = None
    
    if analysis['unique_z_count'] > 1:
        print("\nCác lựa chọn xử lý z:")
        print("1. Giữ nguyên tất cả giá trị z")
        print("2. Thay thế một phần của z cũ bằng z mới")
        print("3. Sử dụng cùng một giá trị z cho tất cả file")
        
        choice = input("\nChọn cách xử lý (1-3): ") or "1"
        
        if choice == "2":
            old_z = input("Nhập phần z cũ cần thay thế: ")
            new_z = input("Nhập phần z mới: ")
        elif choice == "3":
            use_same_z = True
            new_z = input("Nhập giá trị z mới cho tất cả file: ") or f"quiz_{int(time.time())}"
    
    # Đổi tên thư mục
    rename_folder_input = input("\nĐổi tên thư mục? (y/n) [n]: ").lower() or "n"
    rename_folder = rename_folder_input == "y"
    
    print("\nĐang thực hiện đổi tên...")
    
    # Thực hiện đổi tên
    new_folder_path, renamed_count = rename_quiz_files(
        folder_path, 
        old_x, 
        new_x, 
        old_z, 
        new_z, 
        rename_folder, 
        use_same_z,
        start_y  # Thêm tham số start_y
    )
    
    print(f"\nĐã đổi tên {renamed_count} file")
    print(f"Đường dẫn mới sau khi đổi tên: {new_folder_path}")