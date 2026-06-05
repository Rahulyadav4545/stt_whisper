from qdrant_client import QdrantClient

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

# =====================================
# LOAD EMBEDDING MODEL
# =====================================

print("\nLoading embedding model...\n")

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cuda"
)

# =====================================
# LOAD RERANKER
# =====================================

print("\nLoading reranker...\n")

reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3",
    device="cuda"
)

# =====================================
# CONNECT QDRANT
# =====================================

client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "voice_rag"

# =====================================
# USER QUERY LOOP
# =====================================

while True:

    query = input(
        "\nEnter your query (type 'exit' to stop):\n\n"
    )

    if query.lower() == "exit":

        print("\nChat ended.\n")

        break

    # =====================================
    # QUERY EMBEDDING
    # =====================================

    query_embedding = model.encode(

        query,

        normalize_embeddings=True
    ).tolist()

    # =====================================
    # VECTOR SEARCH
    # =====================================

    try:

        results = client.search(

            collection_name=COLLECTION_NAME,

            query_vector=query_embedding,

            limit=10
        )

    except Exception as e:

        print("\nRETRIEVAL ERROR:\n")

        print(e)

        continue

    # =====================================
    # EMPTY CHECK
    # =====================================

    if len(results) == 0:

        print("\nNo results found.\n")

        continue

    # =====================================
    # PREPARE RERANKING
    # =====================================

    pairs = []

    for result in results:

        pairs.append([

            query,

            result.payload["text"]
        ])

    # =====================================
    # RERANK
    # =====================================

    rerank_scores = reranker.predict(
        pairs
    )

    combined = list(
        zip(results, rerank_scores)
    )

    combined.sort(

        key=lambda x: x[1],

        reverse=True
    )

    # =====================================
    # PRINT FINAL RESULTS
    # =====================================

    print("\nRERANKED RESULTS:\n")

    for result, rerank_score in combined:

        print("=" * 80)

        print(
            f"\nVector Score: "
            f"{result.score}"
        )

        print(
            f"Rerank Score: "
            f"{rerank_score}\n"
        )

        payload = result.payload

        print(
            f"Chunk ID: "
            f"{payload['chunk_id']}"
        )

        print(
            f"Start: "
            f"{payload['start']}"
        )

        print(
            f"End: "
            f"{payload['end']}"
        )

        print("\nTEXT:\n")

        print(payload["text"])

        print("\n")