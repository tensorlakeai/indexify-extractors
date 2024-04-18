import re
from langchain.docstore.document import Document

class FastRecursiveTextSplitter:
    def __init__(self, chunk_size=512):
        self.chunk_size = chunk_size

    def create_documents(self, texts):
        chunks = []
        for text in texts:
            chunks.extend(self._divide_text_into_chunks(text))
        converted_list = [Document(page_content=item) for item in chunks]
        return converted_list

    def _divide_text_into_chunks(self, text):
        # Remove leading/trailing whitespace and split the text into words
        words = text.strip().split()
        chunks = []
        current_chunk = []
        current_word_count = 0

        for word in words:
            current_chunk.append(word)
            current_word_count += 1

            if current_word_count >= self.chunk_size:
                # Check if the current word ends with a sentence-ending punctuation
                if re.search(r'[.!?]$', word):
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
                else:
                    # Find the index of the next sentence-ending punctuation
                    next_punct_index = None
                    for i in range(len(words) - len(current_chunk)):
                        if re.search(r'[.!?]$', words[len(current_chunk) + i]):
                            next_punct_index = len(current_chunk) + i + 1
                            break

                    if next_punct_index:
                        # Extend the current chunk to the end of the next sentence
                        current_chunk.extend(words[len(current_chunk):next_punct_index])
                        chunks.append(' '.join(current_chunk))
                        current_chunk = []
                        current_word_count = 0

        # Add the remaining words as the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks