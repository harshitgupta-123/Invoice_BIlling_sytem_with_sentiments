# predict_sentiment.py

import joblib
from preprocess import clean_text

def predict_sentiment(text):
    clf = joblib.load('sentiment_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    
    pred = clf.predict(vec)[0]
    sentiment_map = {1: "Positive", -1: "Negative"}
    return sentiment_map.get(pred, "Unknown")

if __name__ == "__main__":
    print("Type 'stop' to exit.")
    while True:
        text = input("Enter your review: ")
        if text.lower() == "stop":
            print("Exiting...")
            break
        sentiment = predict_sentiment(text)
        print("Predicted Sentiment:", sentiment)
        print("-" * 40)
