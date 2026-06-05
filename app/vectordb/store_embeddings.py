import uuid

from pathlib import Path

from qdrant_client import (
    QdrantClient
)

from qdrant_client.models import (

    Distance,

    VectorParams,

    PointStruct
)
# STORE FUNCTION

def store_embeddings(
    embedded_chunks,
    video_folder
):

    # CONNECT QDRANT

    client = QdrantClient(
        host="localhost",
        port=6333
    )

    COLLECTION_NAME = "voice_rag"

    # VIDEO NAME

    video_name = Path(
        video_folder
    ).name
    youtube_id = video_name
    video_id = video_name

    # CREATE COLLECTION IF MISSING

    collections = (
        client.get_collections().collections
    )

    collection_names = [

        collection.name

        for collection in collections
    ]

    if COLLECTION_NAME not in collection_names:

        client.create_collection(

            collection_name=COLLECTION_NAME,

            vectors_config=VectorParams(

                size=len(
                    embedded_chunks[0]["embedding"]
                ),

                distance=Distance.COSINE
            )
        )

        print(
            f"\nCreated collection: "
            f"{COLLECTION_NAME}"
        )

    else:

        print(
            f"\nUsing existing collection: "
            f"{COLLECTION_NAME}"
        )

    # CREATE POINTS

    points = []

    for chunk in embedded_chunks:

        point = PointStruct(

            id=str(uuid.uuid4()),

            vector=chunk["embedding"],

            payload={

    "chunk_id":
    chunk["chunk_id"],

    "start":
    chunk["start"],

    "end":
    chunk["end"],

    "text":
    chunk["text"],

    "video_name":
    video_name,

    "video_id":
    video_id,

    "youtube_id":
    youtube_id
} 
        )

        points.append(point)

    # INSERT INTO QDRANT

    client.upsert(

        collection_name=COLLECTION_NAME,

        points=points
    )

    # DONE

    print("\nDONE\n")

    print(
        f"Inserted chunks: "
        f"{len(points)}"
    )

    print(
        f"\nVideo stored: "
        f"{video_name}"
    )








    