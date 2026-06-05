from qdrant_client import QdrantClient

from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)


class QdrantVectorDB:

    def __init__(self):

        self.client = QdrantClient(
            path="backend/app/qdrant_db"
        )

        self.collection_name = (
            "audio_chunks"
        )

    def create_collection(
        self,
        vector_size
    ):

        collections = (
            self.client.get_collections()
        )

        existing = [

            col.name
            for col
            in collections.collections
        ]

        if self.collection_name not in existing:

            self.client.create_collection(

                collection_name=
                self.collection_name,

                vectors_config=
                VectorParams(

                    size=vector_size,

                    distance=
                    Distance.COSINE
                )
            )

            print(
                "Qdrant collection created."
            )

        else:

            print(
                "Collection already exists."
            )

    def insert_chunks(
        self,
        chunks,
        embeddings
    ):

        points = []

        for idx, (
            chunk,
            embedding
        ) in enumerate(

            zip(
                chunks,
                embeddings
            )
        ):

            points.append(

                PointStruct(

                    id=idx,

                    vector=
                    embedding.tolist(),

                    payload={

                        "chunk_id":
                        chunk["chunk_id"],

                        "speaker":
                        chunk["speaker"],

                        "start":
                        chunk["start"],

                        "end":
                        chunk["end"],

                        "text":
                        chunk["text"]
                    }
                )
            )

        self.client.upsert(

            collection_name=
            self.collection_name,

            points=points
        )

        print(
            f"Inserted {len(points)} chunks."
        )