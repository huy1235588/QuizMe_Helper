import json
import os
import re


def adjust_quiz_ids(file_path, new_start_question_id, new_start_option_id):
    """
    Adjust question and option IDs in a quiz JSON file to start from specified numbers
    and update image URLs to use question IDs instead of order numbers

    Args:
        file_path (str): Path to the quiz JSON file
        new_start_question_id (int): New starting ID for questions
        new_start_option_id (int): New starting ID for options
    """
    try:
        # Read the original JSON file
        with open(file_path, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_dir, exist_ok=True)

        # Make a backup of the original file in the backup directory
        backup_filename = os.path.basename(file_path) + ".backup"
        backup_path = os.path.join(backup_dir, backup_filename)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
        print(f"Backup saved to {backup_path}")

        # Process each quiz
        for quiz in quiz_data["quizzes"]:
            if "questions" in quiz:
                current_question_id = new_start_question_id
                current_option_id = new_start_option_id

                for question in quiz["questions"]:
                    # Save the original ID to update relations
                    original_question_id = question["id"]

                    # Update question ID
                    question["id"] = current_question_id

                    # Update image URL pattern to use question ID instead of order number
                    if "image_url" in question and question["image_url"]:
                        # Replace quiz_x_question_y with quiz_x_question_id
                        quiz_id = quiz["id"]
                        pattern = f"quiz_{quiz_id}_question_\\d+"
                        replacement = f"quiz_{quiz_id}_question_{current_question_id}"
                        question["image_url"] = re.sub(
                            pattern, replacement, question["image_url"]
                        )

                    # Update options
                    if "options" in question:
                        for option in question["options"]:
                            # Update option ID
                            option["id"] = current_option_id

                            # Update question_id reference in options
                            option["question_id"] = current_question_id

                            current_option_id += 1

                    current_question_id += 1

        # Save the updated JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)

        print(f"Updated {file_path} with new IDs:")
        print(f"- Questions starting from: {new_start_question_id}")
        print(f"- Options starting from: {new_start_option_id}")
        print(f"- Image URLs updated to use question IDs")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":

    file_path = os.path.join(
        "data", "json", "quiz", "geography", "5_Đặc Điểm Tự Nhiên.json"
    )

    try:
        new_start_question_id = int(input("Enter new starting ID for questions: "))
        new_start_option_id = int(input("Enter new starting ID for options: "))

        adjust_quiz_ids(file_path, new_start_question_id, new_start_option_id)
    except ValueError:
        print("Please enter valid integer values for IDs.")
