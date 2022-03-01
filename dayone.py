# Day One app integration

import datetime
import subprocess

DAY_ONE_CMD = 'dayone2'

def saveToDayOne(content: str, mood: str, tags: list[str]) -> str:
    """
    This function constructs and returns a command to be called
    """

    time = datetime.datetime.now().strftime("%H:%M:%S")
    text = f'> `{time}` -- feeling {mood}\n>\n> {content}\n'
    subprocess.Popen([DAY_ONE_CMD, '--tags', *tags, '--', 'new', text])
