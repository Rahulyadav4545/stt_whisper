from qdrant_client import QdrantClient

from qdrant_client.models import (

    Filter,

    FieldCondition,

    MatchValue
)

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

# =====================================
# COLLECTION
# =====================================

COLLECTION_NAME = "voice_rag"

# =====================================
# LOAD MODELS
# =====================================

print("\nLoading embedding model...\n")

embedding_model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cuda"
)

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

# =====================================
# RETRIEVAL FUNCTION
# =====================================

def retrieve_chunks(
    query: str,
    limit: int = 30,
    video_name: str = None
):

    try:

        # =====================================
        # QUERY EMBEDDING
        # =====================================

        formatted_query = (
    f"Represent this sentence for retrieval: {query}"
)

        query_embedding = embedding_model.encode(

            formatted_query,

            normalize_embeddings=True
        ).tolist()

        # =====================================
        # SEARCH CONFIG
        # =====================================

        search_kwargs = {

            "collection_name":
            COLLECTION_NAME,

            "query_vector":
            query_embedding,

            "limit":
            limit
        }

        # =====================================
        # VIDEO FILTER
        # =====================================

        if video_name:

            search_kwargs["query_filter"] = Filter(

                must=[

                    FieldCondition(

                        key="video_name",

                        match=MatchValue(
                            value=video_name
                        )
                    )
                ]
            )

        # =====================================
        # VECTOR SEARCH
        # =====================================

        results = client.search(
            **search_kwargs
        )

        # =====================================
        # EMPTY CHECK
        # =====================================

        if not results:

            return []

        # =====================================
        # VALID RESULTS
        # =====================================

        valid_results = []

        for result in results:

            payload = result.payload

            # =====================================
            # SAFETY CHECKS
            # =====================================

            if not isinstance(payload, dict):
                continue

            if "text" not in payload:
                continue

            if "chunk_id" not in payload:
                continue

            if "video_name" not in payload:
                continue

            valid_results.append(result)

        # =====================================
        # NO VALID RESULTS
        # =====================================

        if not valid_results:

            return []

        # =====================================
        # PREPARE RERANKING
        # =====================================

        pairs = []

        for result in valid_results:

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
            zip(valid_results, rerank_scores)
        )

        combined.sort(

            key=lambda x: x[1],

            reverse=True
        )

        # =====================================
        # FINAL RESULTS
        # =====================================

        final_results = []

        for result, rerank_score in combined[:15]:

            payload = result.payload

            final_results.append({

                "chunk_id":
                payload["chunk_id"],

                "text":
                payload["text"],

                "start":
                payload.get("start", 0),

                "end":
                payload.get("end", 0),

                "vector_score":
                float(result.score),

                "rerank_score":
                float(rerank_score),

                "video_name":
                payload["video_name"]
            })

        return final_results

    # =====================================
    # FAIL SAFE
    # =====================================

    except Exception as e:

        print("\nRETRIEVAL ERROR:\n")

        print(str(e))

        return []