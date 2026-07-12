import pandas as pd
import re

def clean_text(text):
    # Lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_and_preprocess(file_path):
    df = pd.read_csv(file_path)
    # Clean the review text
    df['CleanText'] = df['Summary'].astype(str).apply(clean_text)
    
    # Create sentiment label based on Score (you can customize thresholds)
    df['Sentiment'] = df['Score'].apply(lambda x: 1 if x > 3 else (0 if x == 3 else -1))
    
    # Drop rows with neutral sentiment (optional)
    df = df[df['Sentiment'] != 0]
    
    return df[['CleanText', 'Sentiment']]
