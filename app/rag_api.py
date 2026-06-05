from pathlib import Path

import sys

sys.path.append(
    "/media/ori_quadro/newhd1/Rahul"
)

import ollama

from fastapi import FastAPI

from pydantic import BaseModel

from backend.app.services.retrieval_service import (
    retrieve_chunks
)

from backend.app.pipeline import (
    run_pipeline
)

from backend.app.download.youtube_download import (
    download_youtube_video
)

# =====================================
# FASTAPI APP
# =====================================

app = FastAPI()

# =====================================
# REQUEST MODELS
# =====================================

class ChatRequest(BaseModel):

    query: str

    video_name: str | None = None


class IngestRequest(BaseModel):

    youtube_url: str

# =====================================
# HOME ROUTE
# =====================================

@app.get("/")

def home():

    return {

        "message": "RAG API Running"
    }

# =====================================
# LIST VIDEOS
# =====================================

@app.get("/videos")

def list_videos():

    OUTPUTS_DIR = Path(
        "/media/ori_quadro/newhd1/Rahul/storage/outputs"
    )

    videos = [

        folder.name

        for folder in OUTPUTS_DIR.iterdir()

        if folder.is_dir()
    ]

    return {

        "videos": videos
    }

# =====================================
# VIDEO SUMMARY
# =====================================

@app.get("/summary/{video_name}")

def get_summary(video_name: str):

    summary_path = Path(

        "/media/ori_quadro/newhd1/Rahul/storage/outputs"

    ) / video_name / "video_summary.txt"

    # =====================================
    # FILE CHECK
    # =====================================

    if not summary_path.exists():

        return {

            "error":
            "Summary not found."
        }

    # =====================================
    # LOAD SUMMARY
    # =====================================

    with open(

        summary_path,

        "r",

        encoding="utf-8"

    ) as f:

        summary = f.read()

    # =====================================
    # RESPONSE
    # =====================================

    return {

        "video_name":
        video_name,

        "summary":
        summary
    }

# =====================================
# INGEST YOUTUBE VIDEO
# =====================================

@app.post("/ingest")

def ingest_video(data: IngestRequest):

    youtube_url = data.youtube_url

    # =====================================
    # DOWNLOAD VIDEO
    # =====================================

    video_folder = download_youtube_video(
        youtube_url
    )

    # =====================================
    # RUN FULL PIPELINE
    # =====================================

    run_pipeline(video_folder)

    # =====================================
    # RESPONSE
    # =====================================

    return {

        "message":
        "Video processed successfully.",

        "video_folder":
        video_folder
    }

# =====================================
# CHAT ROUTE
# =====================================

@app.post("/chat")

def chat(data: ChatRequest):

    query = data.query

    # =====================================
    # RETRIEVAL
    # =====================================

    results = retrieve_chunks(

        query=query,

        video_name=data.video_name
    )

    # =====================================
    # SAFETY CHECK
    # =====================================

    if not results:

        return {

            "answer": "No results found."
        }

    # =====================================
    # TOP CONTEXT
    # =====================================

    top_chunks = []

    seen_texts = set()

    for result in results[:5]:

        text = result["text"].strip()

        if text in seen_texts:
            continue

        top_chunks.append(text)

        seen_texts.add(text)

    context = "\n\n".join(top_chunks)

    # =====================================
    # RELEVANCE CHECK
    # =====================================

    top_score = results[0]["rerank_score"]

    if top_score < 0.01:

        return {

            "answer": "Answer not found in videos."
        }

    # =====================================
    # PROMPT
    # =====================================

    prompt = f"""

You are a highly accurate multilingual AI assistant.

Answer ONLY using the provided transcript context.

IMPORTANT:
- If the transcript is Hindi, answer in Hindi.
- If the transcript is English, answer in English.
- If the transcript is Hinglish, answer in Hinglish.

Rules:
- Keep answers concise
- Maximum 3-5 sentences
- Do not hallucinate
- Correct noisy transcript wording automatically
- Use natural conversational language

If answer is missing, say:
"Answer not found in videos."

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
    # SOURCES
    # =====================================

    sources = []

    for result in results[:2]:

        sources.append({

            "video_name": result.get(
                "video_name",
                "unknown"
            ),

            "start": round(
                result["start"],
                2
            ),

            "end": round(
                result["end"],
                2
            )
        })

    # =====================================
    # FINAL RESPONSE
    # =====================================

    return {

        "answer": response["message"]["content"],

        "sources": sources,

        "score": top_score
    }