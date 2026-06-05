import ollama

from backend.app.services.retrieval_service import (
    retrieve_chunks
)

# =====================================
# BUILD CONTEXT
# =====================================

def build_context(results):

    top_chunks = []

    for result in results[:3]:

        top_chunks.append(
            result["text"]
        )

    return "\n\n".join(top_chunks)

# =====================================
# GENERATE ANSWER
# =====================================

def generate_answer(query: str):

    # RETRIEVE CHUNKS

    results = retrieve_chunks(query)

    # BUILD CONTEXT

    context = build_context(results)

    # PROMPT

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
"Answer not found in the provided video."

QUESTION:
{query}

CONTEXT:
{context}

ANSWER:

"""

    # LLM GENERATION

    response = ollama.chat(

        model="qwen2.5:7b",

        messages=[

            {
                "role": "user",

                "content": prompt
            }
        ]
    )

    # RETURN RESPONSE

    return {

        "answer": response["message"]["content"],

        "sources": results[:3]
    }