import unicodedata

def safe_ascii(text, replacement=""):
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    return ascii_text.encode("ascii", "ignore").decode("ascii").replace("?", replacement)
