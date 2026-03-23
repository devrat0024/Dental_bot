from typing import List

class TextChunker:
    def __init__(self, chunk_size: int = 100, overlap: int = 20):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        # Simple character-based chunking that respects newlines
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size * 5 # Approx 5 chars per word
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Find the last newline within the window to keep blocks together
            last_newline = text.rfind('\n', start, end)
            if last_newline != -1 and last_newline > start + (end - start) // 2:
                actual_end = last_newline + 1
            else:
                # Fallback to last space
                last_space = text.rfind(' ', start, end)
                actual_end = last_space + 1 if last_space != -1 else end
            
            chunks.append(text[start:actual_end])
            start = actual_end - (self.overlap * 5) # Approx overlap in chars
            if start < 0: start = 0
            
        return chunks
