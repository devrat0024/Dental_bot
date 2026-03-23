import sys
import os
import numpy as np

# Add the project root to sys.path
sys.path.append(os.getcwd())

from rag_pipeline.ingestion.loader import DataLoader
from rag_pipeline.embedding.tfidf import TFIDFService
from rag_pipeline.vectordb.faiss_manager import VectorDBManager

def run_ingestion():
    print("Starting ingestion...")
    loader = DataLoader("rag_pipeline/data")
    chunks = loader.process_files()
    print(f"Processed {len(chunks)} chunks.")

    texts = [c['text'] for c in chunks]
    
    tfidf = TFIDFService()
    print("Fitting TF-IDF...")
    tfidf.fit(texts)
    vectors = tfidf.transform(texts)
    print(f"Generated vectors with shape {vectors.shape}")

    db = VectorDBManager()
    print("Building FAISS index...")
    db.create_index(vectors, chunks)
    print("Ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
