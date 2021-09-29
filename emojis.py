import csv
from os import read

def read_emojis_list(file_path):
    """Reads the emoji csv and returns a dictionary"""

    with open(file_path, 'r') as emoji_file:
        reader = csv.reader(emoji_file)
        return {rows[1]:rows[0] for rows in reader}


if __name__ == '__main__':
    print(read_emojis_list('emoji.csv'))