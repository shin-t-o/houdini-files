import os
import sys
import re

def concat_files(input_dir, output_file):
    combined_text = ""

    # ファイルを読み込み、結合
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt") and not filename.startswith("_") and not re.search(r"-\d*\.txt$", filename):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r') as infile:
                combined_text += infile.read() + "\n\n==================\n\n\n\n"

    # 不要なインデントを削除
    combined_text = combined_text.replace('    ', '')

    # 修正した内容を出力ファイルに書き込み
    with open(output_file, 'w') as outfile:
        outfile.write(combined_text)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python concat.py [input directory] [output file]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_file = sys.argv[2]

    concat_files(input_dir, output_file)

