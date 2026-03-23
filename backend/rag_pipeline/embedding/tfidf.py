from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

class TFIDFService:
    def __init__(self, model_path: str = "rag_pipeline/embedding/tfidf_model.pkl"):
        self.model_path = model_path
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def fit(self, texts: list):
        self.vectorizer.fit(texts)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)

    def load(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.vectorizer = pickle.load(f)

    def transform(self, texts: list):
        return self.vectorizer.transform(texts).toarray()
