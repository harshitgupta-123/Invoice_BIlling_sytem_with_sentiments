import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
from preprocess import load_and_preprocess

def train_sentiment_model(data_file):
    # Load and preprocess data
    df = load_and_preprocess(data_file)

    # Drop missing values (optional but recommended)
    df.dropna(subset=['CleanText', 'Sentiment'], inplace=True)

    X = df['CleanText']
    y = df['Sentiment']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Vectorize text data using TF-IDF
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Train Random Forest classifier
    clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, n_jobs=-1)
    clf.fit(X_train_vec, y_train)

    # Make predictions
    y_pred = clf.predict(X_test_vec)

    # Evaluation
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    # Save model and vectorizer
    joblib.dump(clf, 'sentiment_model_rf.pkl')
    joblib.dump(vectorizer, 'vectorizer_rf.pkl')

if __name__ == "__main__":
    train_sentiment_model(r'E:\Documents\Coding\Projects\Amazon_Sentiment_Analysis\Data\reviews.csv')
