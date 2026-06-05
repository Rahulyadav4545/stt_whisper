from sentence_transformers import (
    SentenceTransformer
)


class EmbeddingGenerator:

    def __init__(self):

        print(
            "Loading embedding model..."
        )

        self.model = SentenceTransformer(
            "BAAI/bge-m3"
        )

        print(
            "Embedding model loaded."
        )

    def generate_embeddings(
        self,
        chunks
    ):

        texts = [

            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.model.encode(

            texts,

            normalize_embeddings=True,

            show_progress_bar=True
        )

        return embeddings