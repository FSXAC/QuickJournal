
import argparse
import curses
from curses import textpad
from curses.textpad import rectangle
import datetime
import os
from pathlib import Path
import random

import emojis
import autocomplete

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

# Consts
HOME = str(Path.home())

# parameters
MAX_CHARS = 140
PADDING = 1
TITLE = 'QuickJournal'
# TITLE = '😋 QuickJournal'
CURSOR = '\u258e'
BREAK_SEPS = ' '
EMOJIS = os.path.join(HOME, 'Developer/QuickJournal/emoji.csv')
MOODS = ['😣', '🙁', '😐', '🙂', '😁']
MOOD_BRACKET = '[ ' + '   ' * 5 + ']'

# Argument parsing
parser = argparse.ArgumentParser(description='QuickJournal -- rapid and micro journaling.')
parser.add_argument('--live-emojis', help='Enable live-emojis preview', action='store_true')
parser.add_argument('--max-chars', default=140, type=int, help='Maximum number of characters to input')
parser.add_argument('--private', help='Scramble the live text for privacy', action='store_true')

global args
args = parser.parse_args()
MAX_CHARS = args.max_chars

# Randomization
SCRAMBLE_LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
SCRAMBLE_EXCLUDE = [CURSOR, *' ,.!?-\'"']

def writeEntry(txt, mood):
    
    homepath = os.path.join(HOME, 'Documents', 'Journal')
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time = datetime.datetime.now().strftime("%H:%M:%S")

    with open(os.path.join(homepath, f'{date}-qj.md'), 'a') as f:
        f.write(f'\n> `{time}` -- feeling {MOODS[mood]}\n')
        f.write(f'>\n')
        for t in txt.split('\n'):
            f.write(f'> {t}\n')
        f.write(f'\n\n&nbsp;\n')

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


def transformEmojiText(txt, emoji_dict):
    """very broken right now"""
    if ':' not in txt:
        return txt

    colon_indices = [i for i, x in enumerate(txt) if x == ':']

    in_shortcode = False
    start = 0
    new_txt = ''
    for i, ci in enumerate(colon_indices):
        end = ci

        if in_shortcode:
            shortcode = txt[start + 1:end]
            try:
                new_txt += emoji_dict[shortcode]
                end += 1
            except KeyError:
                new_txt += txt[start:end]
        else:
            new_txt += txt[start:end]

        in_shortcode = not in_shortcode
        start = ci

    new_txt += txt[end:]

    return new_txt

def transformText(txt, screen_width, emoji_dict = None, scramble=False):
    # How many characters can we fit inside a line (-1 for border, -1 for cursor)
    max_line_width = screen_width - (2 * PADDING) - 3

    lines = txt.split('\n')
    new_lines = []

    for line in lines:
        
        # If new line (empty)
        if not line:
            new_lines.append(line)
            continue

        # Emoji transform
        if args.live_emojis and emoji_dict:
            line = transformEmojiText(line, emoji_dict)

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
    for i, line in enumerate(split_txt):
        x = 1 + PADDING
        y = 1 + PADDING + i

        for c in line:
            if args.private and c not in SCRAMBLE_EXCLUDE:
                c = random.choice(SCRAMBLE_LETTERS)
            screen.addch(y, x, c)
            x += 1

def drawMoodBar(screen, current_mood: int):
    assert(current_mood in range(len(MOODS)))

    _, width = screen.getmaxyx()
    screen.addstr(0, width - len(MOOD_BRACKET) - 1, MOOD_BRACKET, curses.A_BOLD)

    for i,mood in enumerate(MOODS):
        x = width - len(MOOD_BRACKET) + (3 * i) + 1
        if i == current_mood:
            screen.addch(0, x, mood)
        else:
            screen.addstr(0, x, '·')


def main(screen):

    # Text entry
    txt_entry = ''

    # Mood
    current_mood = len(MOODS) // 2

    # Program state
    done = False

    # Initialize curses stuff
    screen = screen
    curses.curs_set(0)
    height, width = screen.getmaxyx()
    overflow_flag = False

    prev_transform_txt_height = 0
    transform_txt_height = 0

    curses.start_color()
    curses.use_default_colors()

    # emojis list
    emoji_dict = emojis.read_emojis_list(EMOJIS)

    while not done:
        screen.refresh()
        need_refresh = False

        # Text processing
        txt_transformed = transformText(txt_entry, width, emoji_dict=emoji_dict)

        # Draw borders
        vert_offset = len(txt_transformed)
        rect_height = (MAX_CHARS // (width - 2 * PADDING - 2)) + 2 * PADDING + vert_offset
        rectangle(screen, 0, 0, rect_height, width - 1)

        # Draw title over borders
        screen.addstr(0, 1, f'[{TITLE}]', curses.A_BOLD)

        # Mood bar
        drawMoodBar(screen, current_mood)

        # Draw entry text
        # Optimization to refresh screen only when a line break changes
        prev_transform_txt_height = transform_txt_height
        transform_txt_height = len(txt_transformed)
        need_refresh = transform_txt_height != prev_transform_txt_height

        # Actually draw out the text
        drawText(screen, txt_transformed)

        # text limit
        remain_chars = MAX_CHARS - len(txt_entry)
        txt_limit = f'[{remain_chars}]'
        len_text_limit = len(txt_limit)
        txt_limit_x = width - len_text_limit - 1
        if remain_chars >= 0:
            screen.addstr(rect_height, txt_limit_x, txt_limit)
        else:
            screen.addstr(rect_height, txt_limit_x, txt_limit, 
                (curses.A_BLINK | curses.A_REVERSE) if overflow_flag else curses.A_REVERSE)

        # Emoji autocomplete
        current_line = txt_entry.split('\n')[-1]
        current_string = current_line.split(' ')[-1]
        
        if current_string.count(':') % 2 == 1:    # check for open :
            last_colon_index = current_line.rfind(':')
            last_txt = current_line[last_colon_index + 1:]

            if ' ' not in last_txt:
                emoji_suggestions = autocomplete.suggest(emoji_dict, last_txt, num_results=5)
                if emoji_suggestions:
                    need_refresh = True

                    # Calculate the box size
                    max_width = 0
                    for s in emoji_suggestions:
                        if len(s) > max_width:
                            max_width = len(s)
                    
                    emoji_rect_height = len(emoji_suggestions) + 1
                    emoji_rect_width = max_width + 6

                    # Calculate the box position below the cursor
                    # but also to fit inside the window
                    emoji_rect_x = len(current_line) - 1
                    emoji_rect_y = vert_offset + 2
                    rectangle(screen, emoji_rect_y, emoji_rect_x, emoji_rect_y + emoji_rect_height, emoji_rect_x + emoji_rect_width)

                    for i,x in enumerate(emoji_suggestions):
                        screen.addstr(i + emoji_rect_y + 1, emoji_rect_x + 1, f'{emoji_dict[x]} :{x}:'.ljust(max_width + 4))


        # Handle keyboard stuff
        key = screen.getch()

        if key == ESCAPE:
            done = True

        elif key in range(ASCII_MIN, ASCII_MAX):
            # Add ASCII character to the text entry
            txt_entry += chr(key)
        
        elif key == RETURN:
            # new line
            txt_entry += '\n'
            need_refresh = True
        
        elif key == BACKSPACE:
            # Remove character from text entry
            if txt_entry:
                txt_entry = txt_entry[:-1]
                need_refresh = True
                overflow_flag = False

        elif key == CMD_BACKSPACE:
            # Remove a whole word
            space_index = max(txt_entry.rfind(' '), txt_entry.rfind('\n'))

            if space_index == -1:
                txt_entry = ''
            else:
                txt_entry = txt_entry[:space_index]
            
            need_refresh = True

        elif key == LEFT:
            if current_mood == 0:
                current_mood = len(MOODS) - 1
            else:
                current_mood -= 1

        elif key == RIGHT:
            if current_mood == len(MOODS) - 1:
                current_mood = 0
            else:
                current_mood += 1

        elif key == curses.KEY_RESIZE:
            height, width = screen.getmaxyx()
            need_refresh = True

        elif key == SEND:
            if txt_entry:
                if remain_chars >= 0:
                    writeEntry(txt_entry, current_mood)
                    txt_entry = ''
                    need_refresh = True
                    done = True
                else:
                    overflow_flag = True

        if need_refresh:
            screen.clear()
    

if __name__ == '__main__':
    curses.wrapper(main)
