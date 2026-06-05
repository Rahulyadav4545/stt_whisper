import json

from sentence_transformers import (
    SentenceTransformer
)

# =====================================
# LOAD MODEL
# =====================================

print("\nLoading embedding model...\n")

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cuda"
)

# =====================================
# EMBED FUNCTION
# =====================================

def embed_chunks(video_folder):
    chunks_path = (
        f"{video_folder}/semantic_chunks.json"
   
    )

    # =====================================
    # LOAD CHUNKS
    # =====================================

    with open(
        chunks_path,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    # =====================================
    # NORMALIZATION
    # =====================================

    NORMALIZATION_MAP = {

        "मैटो": "Zomato",

        "एपिआई": "API",

        "गूगल मैप्स": "Google Maps",

        "ऊबर": "Uber",

        "ओला": "Ola"
    }

    texts = []

    for chunk in chunks:

        text = chunk["text"]

        for wrong, correct in NORMALIZATION_MAP.items():

            text = text.replace(
                wrong,
                correct
            )

        texts.append(text)

    # =====================================
    # CREATE EMBEDDINGS
    # =====================================

    embeddings = model.encode(

        texts,

        normalize_embeddings=True,

        show_progress_bar=True
    )

    # =====================================
    # CREATE OUTPUT
    # =====================================

    embedded_chunks = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        embedded_chunks.append({

            "chunk_id": chunk["chunk_id"],

            "text": chunk["text"],

            "start": chunk["start"],

            "end": chunk["end"],

            "embedding": embedding.tolist()
        })

    # =====================================
    # DONE
    # =====================================

    print("\nDONE\n")

    print(
        f"Total embedded chunks: "
        f"{len(embedded_chunks)}"
    )

    print(
        f"\nEmbedding dimension: "
        f"{len(embedded_chunks[0]['embedding'])}"
    )

    return embedded_chunks