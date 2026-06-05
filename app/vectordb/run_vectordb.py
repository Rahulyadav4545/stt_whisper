import json
import uuid

from pathlib import Path

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

from sentence_transformers import (
    SentenceTransformer
)

# =====================================
# LOAD EMBEDDING MODEL
# =====================================

print("\nLoading embedding model...\n")

embedding_model = SentenceTransformer(
    "BAAI/bge-m3"
)

# =====================================
# QDRANT CLIENT
# =====================================

client = QdrantClient(

    host="localhost",

    port=6333
)

COLLECTION_NAME = "voice_rag"

# =====================================
# CREATE COLLECTION
# =====================================

existing_collections = client.get_collections()

collection_names = [

    collection.name

    for collection in existing_collections.collections
]

if COLLECTION_NAME not in collection_names:

    print("\nCreating Qdrant collection...\n")

    client.create_collection(

        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(

            size=1024,

            distance=Distance.COSINE
        )
    )

    print("\nCollection created.\n")

# =====================================
# VECTOR DB FUNCTION
# =====================================

def run_vectordb(video_folder):

    video_folder = Path(video_folder)

    # =====================================
    # DUPLICATE CHECK
    # =====================================

    existing = client.scroll(

        collection_name=COLLECTION_NAME,

        limit=1000
    )[0]

    already_exists = False

    for point in existing:

        if (
            point.payload.get("video_name")
            == video_folder.name
        ):

            already_exists = True
            break

    if already_exists:

        print("\nVideo already indexed.\n")

        return

    # =====================================
    # CHUNKS FILE
    # =====================================

    chunks_path = (
        video_folder / "semantic_chunks.json"
    )

    # =====================================
    # CHECK FILE
    # =====================================

    if not chunks_path.exists():

        raise Exception(
            "semantic_chunks.json NOT FOUND"
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
    # EMPTY CHECK
    # =====================================

    if len(chunks) == 0:

        raise Exception(
            "No chunks found."
        )

    # =====================================
    # CREATE POINTS
    # =====================================

    points = []

    for chunk in chunks:

        text = chunk["text"]

        embedding = embedding_model.encode(

            f"Represent this sentence for retrieval: {text}",

            normalize_embeddings=True

        ).tolist()

        point = PointStruct(

            id=str(uuid.uuid4()),

            vector=embedding,

            payload={

                "chunk_id": chunk["chunk_id"],

                "text": text,

                "start": chunk["start"],

                "end": chunk["end"],

                "video_name": video_folder.name
            }
        )

        points.append(point)

    # =====================================
    # UPSERT TO QDRANT
    # =====================================

    client.upsert(

        collection_name=COLLECTION_NAME,

        points=points
    )

    # =====================================
    # DONE
    # =====================================

    print("\nVECTOR DB STEP COMPLETED\n")

    print(f"\nTOTAL POINTS INSERTED: {len(points)}\n")


    