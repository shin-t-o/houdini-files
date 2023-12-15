import os
import json
import re
import sys

def parse_houdini_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    parsed_data = {
        "title": "",
        "type": "",
        "context": "",
        "internal": "",
        "icon": "",
        "tags": [],
        "summary": "",
        "description": "",
        "sections": {}
    }

    # Regular expressions
    title_pattern = r"^=\s([^=]+)\s=$"
    section_pattern = r"^==\s*(.+?)\s*==$"
    at_sign_section_pattern = r"^@(\w+)$"
    summary_pattern = r'^"""(.*?)"""$'
    in_description = False
    current_section = None

    # convert {{{#!xxx}}} to ```xxx````
    if any(re.search(r'^#!', line) for line in lines):
        lines = preprocess_file(lines)
        

    for line in lines:
        line = line.replace('# ', '')
        if re.match(title_pattern, line):
            parsed_data['title'] = re.match(title_pattern, line).group(1)
        elif line.startswith('#'):
            key, value = line.strip('# \n').split(':', 1)
            if key == 'tags':
                parsed_data[key] = [tag.strip() for tag in value.split(',')]
            else:
                parsed_data[key] = value.strip()
        elif re.match(summary_pattern, line):
            parsed_data['summary'] = re.match(summary_pattern, line).group(1)
            in_description = True
        elif re.match(at_sign_section_pattern, line):
            if in_description:
                in_description = False
            current_section = re.match(at_sign_section_pattern, line).group(1)
            parsed_data['sections'][current_section] = ""
        elif in_description:
            parsed_data['description'] += line
        elif re.match(section_pattern, line):
            current_section = re.match(section_pattern, line).group(1)
            parsed_data['sections'][current_section] = ""
        elif current_section:
            parsed_data['sections'][current_section] += line
        parsed_data['node_name'] = parsed_data['internal']

    return json.loads(json.dumps(parsed_data).replace('\\n', ' '))

def preprocess_file(lines):
    # Initialize variables to track the state of the replacement
    in_vex_block = False
    modified_lines = []

    # Process each line
    for line in lines:
        if line.strip() == '{{{':
            in_vex_block = True
            modified_lines.append('```vex')
        elif line.strip() == '}}}' and in_vex_block:
            in_vex_block = False
            modified_lines.append('```')
        elif in_vex_block and line.strip().startswith('#!vex'):
            continue  # Skip the '#!vex' line
        else:
            modified_lines.append(line)

    return modified_lines
    

def parse_houdini_folder(folder_path):
    parsed_files = []
    # parsed_files = {}

    # List all .txt files in the folder
    for file in os.listdir(folder_path):
        if file.endswith(".txt") and not file.startswith("_") and not re.search(r"-\d*\.txt$", file):
            print('file: ', file)
            file_path = os.path.join(folder_path, file)
            parsed_data = parse_houdini_file(file_path)
            # parsed_files[file.replace('.txt', '')] = parsed_data
            parsed_files.append(parsed_data)

    return parsed_files


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_json.py <TEXT_DIR> <OUT.txt>")
        sys.exit(1)

    text_dir = sys.argv[1]
    output_file = sys.argv[2]

    parsed_folder_data = parse_houdini_folder(text_dir)
    json_data = json.dumps(parsed_folder_data, indent=2)

    with open(output_file, 'w') as f:
        f.write(json_data)

if __name__ == "__main__":
    main()