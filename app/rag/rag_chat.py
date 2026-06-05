from qdrant_client import (
    QdrantClient
)

from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue
)

from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder
)

import ollama

# =====================================
# LOAD EMBEDDING MODEL
# =====================================

print("\nLoading embedding model...\n")

embedding_model = SentenceTransformer(
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
# GET AVAILABLE VIDEOS
# =====================================

points, _ = client.scroll(
    collection_name=COLLECTION_NAME,
    limit=1000,
    with_payload=True
)

videos = sorted(
    list(
        set(
            point.payload["video_name"]
            for point in points
        )
    )
)

if len(videos) == 0:

    print("\nNo videos found.\n")
    exit()

print("\n====================================")
print("AVAILABLE VIDEOS")
print("====================================\n")

for idx, video in enumerate(videos, start=1):

    print(
        f"{idx}. {video}"
    )

# =====================================
# SELECT VIDEO
# =====================================

try:

    choice = int(
        input(
            "\nSelect video number:\n\n"
        )
    )

    selected_video = videos[
        choice - 1
    ]

except Exception:

    print("\nInvalid selection.\n")
    exit()

print(
    f"\nSelected Video:\n{selected_video}\n"
)

# =====================================
# USER QUERY
# =====================================

query = input(
    "\nAsk your question:\n\n"
)

# =====================================
# QUERY EMBEDDING
# =====================================

query_embedding = embedding_model.encode(

    f"Represent this sentence for retrieval: {query}",

    normalize_embeddings=True

).tolist()

# =====================================
# VECTOR SEARCH
# =====================================

results = client.search(

    collection_name=COLLECTION_NAME,

    query_vector=query_embedding,

    limit=20,

    query_filter=Filter(
        must=[
            FieldCondition(
                key="video_name",
                match=MatchValue(
                    value=selected_video
                )
            )
        ]
    )
)

if len(results) == 0:

    print(
        "\nAnswer not found in the selected video.\n"
    )

    exit()

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
    zip(
        results,
        rerank_scores
    )
)

combined.sort(
    key=lambda x: x[1],
    reverse=True
)

best_score = combined[0][1]

if best_score < 0.15:

    print("\nFINAL ANSWER:\n")

    print(
        "Answer not found in the selected video."
    )

    exit()

# =====================================
# TOP CONTEXT
# =====================================

top_chunks = []

for result, score in combined[:5]:

    top_chunks.append(
        result.payload["text"]
    )

context = "\n\n".join(
    top_chunks
)

# =====================================
# PROMPT
# =====================================

prompt = f"""

You are a highly accurate multilingual AI assistant.

Answer ONLY using the provided transcript context.

IMPORTANT:

- Reply in the SAME language style as the user's question.
- If the user asks in English, reply in English.
- If the user asks in Hinglish, reply in Hinglish.
- Keep technical terms in English.
- Sound natural like a tech educator.

Rules:

- Keep answers concise
- Maximum 3-5 sentences
- Do not hallucinate
- Do not repeat information
- Do not copy transcript text directly
- Correct noisy transcript wording automatically

If answer is missing, say:

Answer not found in the provided video.

VIDEO:
{selected_video}

QUESTION:
{query}

CONTEXT:
{context}

ANSWER:

"""

# =====================================
# LLM GENERATION
# =====================================

response = ollama.chat(

    model="qwen2.5:7b",

    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# =====================================
# FINAL ANSWER
# =====================================

print("\n====================================")
print("FINAL ANSWER")
print("====================================\n")

print(
    response["message"]["content"]
)

# =====================================
# SOURCES
# =====================================

print("\n====================================")
print("SOURCES")
print("====================================\n")

for result, score in combined[:5]:

    start = round(
        result.payload["start"],
        2
    )

    end = round(
        result.payload["end"],
        2
    )

    video_name = (
        result.payload["video_name"]
    )

    print(video_name)

    print(
        f"{start}s → {end}s"
    )

    print()