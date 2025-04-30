import json
import os

def adjust_quiz_ids(file_path, new_start_question_id, new_start_option_id):
    """
    Adjust question and option IDs in a quiz JSON file to start from specified numbers
    
    Args:
        file_path (str): Path to the quiz JSON file
        new_start_question_id (int): New starting ID for questions
        new_start_option_id (int): New starting ID for options
    """
    try:
        # Read the original JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            quiz_data = json.load(f)
        
        # Make a backup of the original file
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
        print(f"Backup saved to {backup_path}")
        
        # Process each quiz
        for quiz in quiz_data['quizzes']:
            if 'questions' in quiz:
                current_question_id = new_start_question_id
                current_option_id = new_start_option_id
                
                for question in quiz['questions']:
                    # Save the original ID to update relations
                    original_question_id = question['id']
                    
                    # Update question ID
                    question['id'] = current_question_id
                    
                    # Update options
                    if 'options' in question:
                        for option in question['options']:
                            # Update option ID
                            option['id'] = current_option_id
                            
                            # Update question_id reference in options
                            option['question_id'] = current_question_id
                            
                            current_option_id += 1
                    
                    current_question_id += 1
        
        # Save the updated JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
        
        print(f"Updated {file_path} with new IDs:")
        print(f"- Questions starting from: {new_start_question_id}")
        print(f"- Options starting from: {new_start_option_id}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    
    file_path = os.path.join("data", "json", "quiz", "địa danh nổi tiếng.json")
    
    try:
        new_start_question_id = int(input("Enter new starting ID for questions: "))
        new_start_option_id = int(input("Enter new starting ID for options: "))
        
        adjust_quiz_ids(file_path, new_start_question_id, new_start_option_id)
    except ValueError:
        print("Please enter valid integer values for IDs.")