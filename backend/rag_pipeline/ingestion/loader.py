import os
from .cleaner import DataCleaner
from .chunker import TextChunker

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.cleaner = DataCleaner()
        self.chunker = TextChunker()

    def process_files(self):
        all_chunks = []
        for filename in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, filename)
            if os.path.isfile(file_path) and filename.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    cleaned_text = self.cleaner.clean_text(text)
                    chunks = self.chunker.chunk_text(cleaned_text)
                    for i, chunk in enumerate(chunks):
                        all_chunks.append({
                            "id": f"{filename}_{i}",
                            "text": chunk,
                            "source": filename,
                            "page": "N/A"
                        })
        return all_chunks
