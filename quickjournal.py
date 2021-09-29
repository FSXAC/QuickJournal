
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
MAX_CHARS = 140
PADDING = 1
TITLE = '😋 QuickJournal'
CURSOR = '\u258e'
BREAK_SEPS = ' '

def writeEntry(txt):
    home = str(Path.home())
    homepath = os.path.join(home, 'Documents', 'Journal')
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")

    with open(os.path.join(homepath, f'{date}.md'), 'a') as f:
        f.write(f'\n`{time}`\n\n')
        f.write(txt)
        f.write('---\n')

def findBreakIndex(txt, max_width):
    """
    Given a long string, and maximimum width,
    find the appropriate line break index(es)

    Accepted separators include spaces and punctuations
    """

    if len(txt) <= max_width:
        return []

    part_txt = txt[:max_width]
    txt_mask = ''.join(['0' if c in BREAK_SEPS else '1' for c in part_txt])
    index = max_width - 1
    while index > 0:
        if txt_mask[index] == '0' and txt_mask[index - 1] == '1':
            break
        else:
            index -= 1

    remaining_txt = txt[index + 1:]
    
    return [index] + findBreakIndex(remaining_txt, max_width)


def transformText(txt, screen_width):
    # How many characters can we fit inside a line (-1 for border, -1 for cursor)
    max_line_width = screen_width - (2 * PADDING) - 3

    lines = txt.split('\n')
    new_lines = []

    for line in lines:
        
        # If new line (empty)
        if not line:
            new_lines.append(line)
            continue

        # Not suppose to be here, shoudl be per line txt
        breaks = findBreakIndex(line, max_line_width)

        if breaks:
            # Display the first line
            new_lines.append(line[:breaks[0]])

            for i in range(len(breaks)):
                line = line[breaks[i] + 1:]

                if (i == len(breaks) - 1):
                    segment = line
                else:
                    segment = line[:breaks[i + 1]]
                
                new_lines.append(segment)
        else:
            new_lines.append(line)

    # Add cursor at the back
    new_lines[-1] += CURSOR

    return new_lines

def drawText(screen, split_txt):
    """Handles rendering of the main text, including line and word breaks"""

    need_refresh = False

    for i, line in enumerate(split_txt):
        screen.addstr(1 + PADDING + i, 1 + PADDING, line)

    return need_refresh

def main(screen):

    # Text entry
    txt_entry = ''

    # Program state
    done = False

    # Initialize curses stuff
    screen = screen
    curses.curs_set(0)
    height, width = screen.getmaxyx()

    prev_transform_txt_height = 0
    transform_txt_height = 0

    curses.start_color()
    curses.use_default_colors()

    while not done:
        screen.refresh()
        need_refresh = False

        # Draw borders
        vert_offset = len(transformText(txt_entry, width))
        rect_height = (MAX_CHARS // (width - 2 * PADDING - 2)) + 2 * PADDING + vert_offset
        rectangle(screen, 0, 0, rect_height, width - 1)

        # Draw title over borders
        screen.addstr(0, 1, f'[{TITLE}]', curses.A_BOLD)

        # Draw entry text
        # Optimization to refresh screen only when a line break changes
        txt_transformed = transformText(txt_entry, width)
        prev_transform_txt_height = transform_txt_height
        transform_txt_height = len(txt_transformed)
        need_refresh = transform_txt_height != prev_transform_txt_height

        # Actually draw out the text
        drawText(screen, txt_transformed)

        # text limit
        chars = len(txt_entry)
        txt_limit = f'[{chars}/{MAX_CHARS}]'
        if chars < MAX_CHARS:
            screen.addstr(rect_height, 1, txt_limit)
        else:
            screen.addstr(rect_height, 1, txt_limit, curses.A_REVERSE)

        # Handle keyboard stuff
        key = screen.getch()

        if key == ESCAPE:
            done = True

        elif key in range(ASCII_MIN, ASCII_MAX):
            # Add ASCII character to the text entry
            if chars < MAX_CHARS:
                txt_entry += chr(key)
        
        elif key == RETURN:
            # new line
            if chars < MAX_CHARS:
                txt_entry += '\n'
                need_refresh = True
        
        elif key == BACKSPACE:
            # Remove character from text entry
            if txt_entry:
                txt_entry = txt_entry[:-1]
                need_refresh = True

        elif key == CMD_BACKSPACE:
            # Remove a whole word
            space_index = max(txt_entry.rfind(' '), txt_entry.rfind('\n'))

            if space_index == -1:
                txt_entry = ''
            else:
                txt_entry = txt_entry[:space_index]
            
            need_refresh = True

        elif key == curses.KEY_RESIZE:
            height, width = screen.getmaxyx()
            need_refresh = True

        elif key == SEND:
            if txt_entry:
                writeEntry(txt_entry)
                txt_entry = ''
                need_refresh = True

        if need_refresh:
            screen.clear()
    

if __name__ == '__main__':
    curses.wrapper(main)