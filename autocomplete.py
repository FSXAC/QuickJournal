import emojis

def suggest(dictionary, txt, num_results=10):
    """
    Given a dictionary and some input text (txt), suggest a set of auto-
    complete suggestions
    """

    if not txt:
        return []

    primaries = []
    secondaries = []

    for shortcode, emoji in dictionary.items():
        if shortcode.startswith(txt):
            primaries.append(shortcode)

        elif txt in shortcode:
            secondaries.append(shortcode)

    # Sort the top candidates and create an output dict
    # combine the two and truncate to num_results
    candidates = sorted(primaries) + sorted(secondaries)
    return candidates[:num_results]


if __name__ == '__main__':
    emoji_dict = emojis.read_emojis_list('emoji.csv')
    while True:
        txt = input("Enter: ")
        suggestions = suggest(emoji_dict, txt)
        for s in suggestions:
            print(emoji_dict[s], f':{s}:')
            
