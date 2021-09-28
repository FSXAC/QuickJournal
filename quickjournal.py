
import curses
from curses import textpad
from curses.textpad import rectangle
import datetime
import os
from pathlib import Path
import sys

# keys
SEND = 7
TAB = 9
CMD_BACKSPACE = 21
ESCAPE = 27
BACKSPACE = 127
RETURN = 10

DOWN = 258
UP = 259
LEFT = 260
RIGHT = 261

ASCII_MIN = 32
ASCII_MAX = 127

# parameters
MAX_CHARS = 280
TITLE = '😋 QuickJournal'

def writeEntry(txt):
    home = str(Path.home())
    homepath = os.path.join(home, 'Documents', 'Journal')
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")

    with open(os.path.join(homepath, f'{date}.md'), 'a') as f:
        f.write(f'\n`{time}`\n\n')
        f.write(txt.replace('\n', '\n\n'))
        f.write('---\n')


def main(screen):

    # Text entry
    txt_entry = ''

    # Program state
    done = False

    # Initialize curses stuff
    screen = screen
    curses.curs_set(0)
    height, width = screen.getmaxyx()

    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    while not done:
        screen.refresh()

        vert_offset = txt_entry.count('\n')
        height = (MAX_CHARS // width) + 1 + vert_offset
        rectangle(screen, 0, 0, height, width - 1)

        screen.addstr(0, 1, f'[{TITLE}]')

        # Draw entry text
        for i, txt in enumerate(txt_entry.split('\n')):
            screen.addstr(1 + i, 1, txt)

        current_line_length = len(txt_entry.split('\n')[-1])
        screen.addch(1 + vert_offset, current_line_length + 1, '_')

        # text limit
        txt_limit = f'{len(txt_entry)}/{MAX_CHARS}'
        screen.addstr(height, 1, txt_limit)

        # Handle keyboard stuff
        key = screen.getch()

        if key == ESCAPE:
            done = True

        elif key in range(ASCII_MIN, ASCII_MAX):
            # Add ASCII character to the text entry
            txt_entry += chr(key)
            
            # Refresh screen
            # screen.clear()
        
        elif key == RETURN:
            # new line
            txt_entry += '\n'
            screen.clear()
        
        elif key == BACKSPACE:
            # Remove character from text entry
            if txt_entry:
                txt_entry = txt_entry[:-1]
                screen.clear()

        elif key == CMD_BACKSPACE:
            # Remove a whole word
            space_index = max(txt_entry.rfind(' '), txt_entry.rfind('\n'))

            if space_index == -1:
                txt_entry = ''
            else:
                txt_entry = txt_entry[:space_index]
            
            screen.clear()

        elif key == curses.KEY_RESIZE:
            height, width = screen.getmaxyx()
            screen.clear()

        elif key == SEND:
            if txt_entry:
                writeEntry(txt_entry)
                txt_entry = ''
                screen.clear()
    

if __name__ == '__main__':
    curses.wrapper(main)