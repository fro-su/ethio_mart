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



import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.char_classes import ALPHA
from spacy.util import compile_infix_regex
import pandas as pd

def tokenize_messages(df, column_name):
    # Load a base model (e.g., English) to use for custom tokenization
    nlp = spacy.blank('en')

    # Customize the tokenizer
    infixes = (ALPHA,)  # Use alpha characters only (basic Amharic chars)
    infix_re = compile_infix_regex(infixes)
    nlp.tokenizer = Tokenizer(nlp.vocab, infix_finditer=infix_re.finditer)

    # Ensure that all values in the specified column are strings
    df[column_name] = df[column_name].astype(str)

    # Tokenize each message using spaCy
    df['tokenized'] = df[column_name].apply(lambda x: [token.text for token in nlp(x)])

    return df[['Message', 'tokenized']]

def label_messages_with_birr(df, column_name):
    def label_message_utf8_with_birr(message):
        # Split the message at the first occurrence of '\n'
        if '\n' in message:
            first_line, remaining_message = message.split('\n', 1)
        else:
            first_line, remaining_message = message, ""
        
        labeled_tokens = []
        
        # Tokenize the first line
        first_line_tokens = re.findall(r'\S+', first_line)
        
        # Label the first token as B-PRODUCT and the rest as I-PRODUCT
        if first_line_tokens:
            labeled_tokens.append(f"{first_line_tokens[0]} B-PRODUCT")  # First token as B-PRODUCT
            for token in first_line_tokens[1:]:
                labeled_tokens.append(f"{token} I-PRODUCT")  # Remaining tokens as I-PRODUCT
        
        # Process the remaining message normally
        if remaining_message:
            lines = remaining_message.split('\n')
            for line in lines:
                tokens = re.findall(r'\S+', line)  # Tokenize each line while considering non-ASCII characters
                
                for token in tokens:
                    # Check if token is a phone number (e.g., 10 consecutive digits)
                    if re.match(r'^\d{10}$', token):
                        labeled_tokens.append(f"{token} I-PHONE")  # Label as I-PHONE
                    
                    # Check if token is a price (e.g., 500 ETB, $100, or ብር)
                    elif re.match(r'^\d+(\.\d{1,2})?$', token) or 'ETB' in token or 'ዋጋ' in token or '$' in token or 'ብር' in token or 'birr' in token:
                        labeled_tokens.append(f"{token} I-PRICE")
                    
                    # Check if token could be a location (e.g., cities or general location names)
                    elif any(loc in token for loc in ['Addis Ababa', 'ለቡ', 'ለቡ መዳህኒዓለም', 'መገናኛ', 'ቦሌ', 'ሜክሲኮ', 'ብስራተ', 'ገብርኤል', 'ገርጂ', 'ኢምፔሪያል', 'ህንፃ', 'ፕላዛ', '4ኪሎ', 'ፎቅ', 'ላፍቶ', 'ሞል', 'ስላሴ']):
                        labeled_tokens.append(f"{token} I-LOC")
                    
                    # Assume other tokens are part of a product name or general text
                    else:
                        labeled_tokens.append(f"{token} O")
        
        return "\n".join(labeled_tokens)
    
    # Apply the labeling function to the specified column
    df['Labeled_Message'] = df[column_name].apply(label_message_utf8_with_birr)

    return df


def load_labeled_data(file_name, base_path='../data', encoding='utf-8', delimiter='\t'):
    # Define the data path
    data_path = os.path.join(base_path, file_name)

    # Try specifying the encoding
    with open(data_path, 'r', encoding=encoding, errors='replace') as file:
        lines = file.readlines()

    # Process lines as needed, using the specified delimiter
    data = [line.strip().split(delimiter) for line in lines]  # Adjust the split based on your delimiter

    # Create a DataFrame, assuming the first column is 'Labeled_Message'
    labeled_data = pd.DataFrame(data, columns=['Labeled_Message'])

    return labeled_data

def extract_tokens_and_labels(labeled_data):
    tokens = []
    labels = []

    # Iterate over the DataFrame to split the 'Labeled_Message' column
    for message in labeled_data['Labeled_Message']:
        parts = message.split()  # Split the string by whitespace
        if len(parts) == 2:      # Ensure that line has exactly two parts
            token = parts[0]      # The token (first part)
            label = parts[1]      # The label (second part)
            tokens.append(token)
            labels.append(label)

    # Create a new DataFrame with the separated tokens and labels
    df_labeled = pd.DataFrame({
        'Token': tokens,
        'Label': labels
    })

    return df_labeled