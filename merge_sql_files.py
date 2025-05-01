import os

def merge_sql_files(input_directory, output_file):
    """Merge multiple SQL files into a single SQL file."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(input_directory):
            if filename.endswith('.sql'):
                file_path = os.path.join(input_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write('\n')  # Add a newline between files

def main():
    input_directory = 'data/sql'  # Specify the directory containing SQL files
    output_file = os.path.join(input_directory, 'merged_sql.sql')  # Specify the output file name
    merge_sql_files(input_directory, output_file)
    print(f'Merged SQL files into {output_file}')

if __name__ == '__main__':
    main()