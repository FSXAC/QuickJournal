
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


def drawText(screen, screen_width, txt):
    """Handles rendering of the main text, including line and word breaks"""

    need_refresh = False

    # How many characters can we fit inside a line (-1 for border, -1 for cursor)
    max_line_width = screen_width - (2 * PADDING) - 3

    lines = txt.split('\n')
    break_offset = 0

    # Cursor position
    cursor_x = 0

    for line in lines:

        # Not suppose to be here, shoudl be per line txt
        breaks = findBreakIndex(line, max_line_width)

        if breaks:
            # Display the first line
            segment = line[:breaks[0]]
            screen.addstr(1 + PADDING + break_offset, 1 + PADDING, segment)

            for i in range(len(breaks)):
                break_offset += 1
                line = line[breaks[i] + 1:]

                if (i == len(breaks) - 1):
                    segment = line
                else:
                    segment = line[:breaks[i + 1]]
                
                screen.addstr(1 + PADDING + break_offset, 1 + PADDING, segment)
                cursor_x = len(segment)
        else:
            screen.addstr(1 + PADDING + break_offset, 1 + PADDING, line)
            cursor_x = len(line)

        break_offset += 1
    
    screen.addch( PADDING + break_offset, cursor_x + 2, '\u258e')
    
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

    curses.start_color()
    curses.use_default_colors()

    while not done:
        screen.refresh()
        need_refresh = False

        # Draw borders
        vert_offset = txt_entry.count('\n')
        rect_height = (MAX_CHARS // (width - 2 * PADDING - 2)) + 2 * PADDING + vert_offset
        rectangle(screen, 0, 0, rect_height, width - 1)

        # Draw title over borders
        screen.addstr(0, 1, f'[{TITLE}]')

        # Draw entry text
        need_refresh |= drawText(screen, width, txt_entry)

        # current_line_length = len(txt_entry.split('\n')[-1])
        # screen.addch(1 + vert_offset, current_line_length + 1, '\u258e')

        # text limit
        txt_limit = f'[{len(txt_entry)}/{MAX_CHARS}]'
        screen.addstr(rect_height, 1, txt_limit)

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
            txt_entry += '\n\n'
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