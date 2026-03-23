from ..embedding.tfidf import TFIDFService
from ..vectordb.faiss_manager import VectorDBManager

class RetrievalService:
    def __init__(self):
        self.tfidf = TFIDFService()
        self.db = VectorDBManager()
        self.tfidf.load()
        self.db.load()

    def search(self, query: str, k: int = 3):
        query_vec = self.tfidf.transform([query])
        return self.db.search(query_vec, k)
