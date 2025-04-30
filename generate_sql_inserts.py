import json
import os

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def generate_inserts(json_data):
    """Generate SQL INSERT statements from JSON data."""
    sql_statements = []
    
    # Add transaction begin
    sql_statements.append("START TRANSACTION;")
    
    # Process quizzes
    for quiz in json_data.get('quizzes', []):
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
        
        # Insert quiz_category relationship
        quiz_category_insert = f"""
INSERT INTO quiz_category (quiz_id, category_id)
VALUES ({quiz['id']}, {quiz['category_id']});
"""
        sql_statements.append(quiz_category_insert)
        
        # Process questions
        if 'questions' in quiz:
            for question_group in quiz['questions']:
                for question in question_group.get('questions', []):
                    # Insert question
                    image_url = f"'{question['image_url']}'" if question['image_url'] else "NULL"
                    audio_url = f"'{question['audio_url']}'" if question['audio_url'] else "NULL"
                    
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
                    
                    # Process options
                    for option in question.get('options', []):
                        option_insert = f"""
INSERT INTO question_option (id, question_id, content, is_correct)
VALUES ({option['id']}, 
        {option['question_id']}, 
        '{option['content'].replace("'", "''")}', 
        {str(option['is_correct']).lower()});
"""
                        sql_statements.append(option_insert)
    
    # Process autocomplete_hints
    for hint in json_data.get('autocomplete_hints', []):
        hint_insert = f"""
INSERT INTO autocomplete_hint (id, content, priority)
VALUES ({hint['id']}, 
        '{hint['content'].replace("'", "''")}', 
        {hint['priority']});
"""
        sql_statements.append(hint_insert)
    
    # Add transaction commit
    sql_statements.append("COMMIT;")
    
    return "\n".join(sql_statements)

def save_sql(sql_content, output_path):
    """Save the SQL content to a file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(sql_content)

def main():
    # Define paths
    json_directory = os.path.join('data', 'json', 'category')
    output_directory = os.path.join('data', 'sql')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Process each JSON file in the directory
    # for filename in os.listdir(json_directory):
    #     if filename.endswith('.json'):
    filename = '7_sports.json' 
    json_path = os.path.join(json_directory, filename)
    output_name = f"{os.path.splitext(filename)[0]}_inserts.sql"
    output_path = os.path.join(output_directory, output_name)
    
    print(f"Processing {json_path}...")
    json_data = load_json(json_path)
    sql_content = generate_inserts(json_data)
    save_sql(sql_content, output_path)
    print(f"SQL inserts saved to {output_path}")

if __name__ == "__main__":
    main()