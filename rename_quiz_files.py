import os
import re

def rename_quiz_files(folder_path, old_x, new_x, rename_folder=False):
    """
    Đổi tên các file có dạng quiz_x_question_y_z hoặc quiz_thumbnail_x_z 
    thành quiz_new_x_question_y_z hoặc quiz_thumbnail_new_x_z
    
    Args:
        folder_path: Đường dẫn đến thư mục chứa các file
        old_x: Giá trị x hiện tại cần thay đổi
        new_x: Giá trị x mới
        rename_folder: Có đổi tên thư mục hay không
    """
    # Mẫu regex để tìm các file dạng quiz_x_question_y_z
    pattern_question = re.compile(f"quiz_{old_x}_question_(\d+)_(.+)")
    
    # Mẫu regex để tìm các file dạng quiz_thumbnail_x_z
    pattern_thumbnail = re.compile(f"quiz_thumbnail_{old_x}_(.+)")
    
    # Liệt kê tất cả các file trong thư mục
    for filename in os.listdir(folder_path):
        # Kiểm tra file dạng quiz_x_question_y_z
        match_question = pattern_question.match(filename)
        if match_question:
            y = match_question.group(1)  # Lấy giá trị y
            z = match_question.group(2)  # Lấy phần z
            
            # Tạo tên file mới
            new_filename = f"quiz_{new_x}_question_{y}_{z}"
            
            # Đường dẫn đầy đủ cho file cũ và mới
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Đổi tên file
            os.rename(old_path, new_path)
            print(f"Đã đổi tên: {filename} -> {new_filename}")
            continue
        
        # Kiểm tra file dạng quiz_thumbnail_x_z
        match_thumbnail = pattern_thumbnail.match(filename)
        if match_thumbnail:
            z = match_thumbnail.group(1)  # Lấy phần z
            
            # Tạo tên file mới
            new_filename = f"quiz_thumbnail_{new_x}_{z}"
            
            # Đường dẫn đầy đủ cho file cũ và mới
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            
            # Đổi tên file
            os.rename(old_path, new_path)
            print(f"Đã đổi tên thumbnail: {filename} -> {new_filename}")
    
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
            
            # Tạo tên thư mục mới (thay đổi số)
            new_folder_name = f"{new_x}_{folder_name}"
            new_folder_path = os.path.join(parent_dir, new_folder_name)
            
            # Đổi tên thư mục
            os.rename(folder_path, new_folder_path)
            print(f"Đã đổi tên thư mục: {current_folder_name} -> {new_folder_name}")
            return new_folder_path
    
    return folder_path

if __name__ == "__main__":
    # Thư mục chứa các file quiz
    folder_path = "data/test/1"  

    # Nhập giá trị x cũ và x mới
    old_x = 123
    new_x = 1
    
    # Đổi tên cả thư mục nếu cần
    rename_folder = True
    
    # Thực hiện đổi tên
    new_folder_path = rename_quiz_files(folder_path, old_x, new_x, rename_folder)
    print(f"Đường dẫn mới sau khi đổi tên: {new_folder_path}")