import json

from pathlib import Path

import ollama

# =====================================
# SUMMARY FUNCTION
# =====================================

def generate_video_summary(video_folder):

    # =====================================
    # LOAD CHUNKS
    # =====================================

    chunk_path = Path(
        video_folder
    ) / "semantic_chunks.json"

    with open(
        chunk_path,
        "r",
        encoding="utf-8"
    ) as f:

        chunks = json.load(f)

    # =====================================
    # SECTION CONFIG
    # =====================================

    SECTION_SIZE = 10

    # =====================================
    # SECTION SUMMARIES
    # =====================================

    chunk_summaries = []

    for i in range(
        0,
        len(chunks),
        SECTION_SIZE
    ):

        print(
            f"\nSummarizing section "
            f"{(i // SECTION_SIZE) + 1}"
        )

        # =====================================
        # SECTION CHUNKS
        # =====================================

        section_chunks = chunks[
            i:i + SECTION_SIZE
        ]

        # =====================================
        # COMBINE TEXT
        # =====================================

        text = "\n\n".join(

            chunk["text"]

            for chunk in section_chunks
        )

        # =====================================
        # SECTION PROMPT
        # =====================================

        prompt = f"""

Summarize this transcript section.

Requirements:

- Preserve important technical concepts
- Maintain chronological teaching flow
- Remove filler speech
- Keep examples and explanations
- Write naturally and clearly
- Keep educational value high
- Avoid robotic bullet formatting

TRANSCRIPT:
{text}

SECTION SUMMARY:

"""

        # =====================================
        # LLM CALL
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

        summary = (
            response["message"]["content"]
        )

        # =====================================
        # STORE SECTION SUMMARY
        # =====================================

        chunk_summaries.append({

            "section_id":
            i // SECTION_SIZE,

            "start":
            section_chunks[0]["start"],

            "end":
            section_chunks[-1]["end"],

            "summary":
            summary
        })

    # =====================================
    # COMBINE SECTION SUMMARIES
    # =====================================

    combined_summary = "\n\n".join(

        item["summary"]

        for item in chunk_summaries
    )

    # =====================================
    # FINAL VIDEO SUMMARY PROMPT
    # =====================================

    final_prompt = f"""

Create a high-quality educational summary
of the full video.

Requirements:

- Explain concepts deeply but clearly
- Preserve teaching flow
- Merge repeated ideas naturally
- Avoid robotic bullet formatting
- Keep practical explanations
- Include examples when relevant
- Explain WHY concepts matter
- Maintain chronological progression
- Write like a professional technical educator
- Keep technical accuracy high
- Remove repetitive filler

Structure:

1. Introduction
2. Core concepts explained
3. Technical workflow/details
4. Practical applications
5. Important takeaways

Write polished readable paragraphs
with clean section headings.

VIDEO CONTENT:
{combined_summary}

FINAL SUMMARY:

"""

    # =====================================
    # FINAL LLM CALL
    # =====================================

    final_response = ollama.chat(

        model="qwen2.5:7b",

        messages=[

            {
                "role": "user",

                "content": final_prompt
            }
        ]
    )

    final_summary = (
        final_response["message"]["content"]
    )

    # =====================================
    # SAVE FINAL SUMMARY
    # =====================================

    output_path = Path(
        video_folder
    ) / "video_summary.txt"

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(final_summary)

    print("\nSUMMARY SAVED\n")

    return final_summary