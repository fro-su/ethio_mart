import re

# Define function to remove emojis,white white space, characters and english letters
def clean_text(text):
    # A broad regex pattern to match most emojis
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\u2600-\u26FF"          # Miscellaneous Symbols
        "\u2700-\u27BF"          # Dingbats
        "\u2B50"                 # Star
        "\u2764-\u2767"         # Hearts
        "\U00002702-\U000027B0" # Miscellaneous Symbols and Arrows
        "\U0001F1E6-\U0001F1FF"  # Regional Indicator Symbols (Flags)
        "]+", flags=re.UNICODE)

    # Remove emojis
    text = emoji_pattern.sub(r'', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove '\n' characters
    text = text.replace('\\n', ' ')
    
    # Remove English letters
    text = re.sub(r'[a-zA-Z]', '', text)
    
    return text

