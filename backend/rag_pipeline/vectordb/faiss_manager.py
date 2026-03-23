import faiss
import numpy as np
import pickle
import os

class VectorDBManager:
    def __init__(self, index_path: str = "rag_pipeline/vectordb/faiss_index.idx", 
                 chunks_path: str = "rag_pipeline/vectordb/chunks.pkl"):
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.index = None
        self.chunks = []

    def create_index(self, vectors: np.ndarray, chunks: list):
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(vectors.astype('float32'))
        self.chunks = chunks
        
        # Save
        faiss.write_index(self.index, self.index_path)
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)

    def load(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)

    def search(self, query_vector: np.ndarray, k: int = 3):
        if self.index is None:
            return []
        distances, indices = self.index.search(query_vector.astype('float32'), k)
        results = []
        for i in indices[0]:
            if i != -1:
                results.append(self.chunks[i])
        return results
