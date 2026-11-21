"""Telugu script -> Devanagari (phonetic, letter-for-letter) so a Hindi-capable TTS can speak Telugu words."""
SPECIAL = {'ె': 'े', 'ొ': 'ो', 'ఎ': 'ए', 'ఒ': 'ओ',  # short e/o -> e/o
           'ఱ': 'र', 'ౘ': 'स', 'ౙ': 'ज', 'ౕ': '', 'ౖ': 'ै'}
def te2dev(s):
    out = []
    for ch in s:
        c = ord(ch)
        if ch in SPECIAL: out.append(SPECIAL[ch])
        elif 0x0C00 <= c <= 0x0C7F: out.append(chr(c - 0x0300))
        else: out.append(ch)
    return ''.join(out)
if __name__ == '__main__':
    import sys; sys.stdout.reconfigure(encoding='utf-8'); print(te2dev(sys.argv[1]))
