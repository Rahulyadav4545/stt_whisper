import json

from backend.app.chunking.semantic_chunker import (
    create_semantic_chunks
)

# =====================================
# CHUNKING FUNCTION
# =====================================

def run_chunking(video_folder):

    print("\nUSING VIDEO FOLDER:\n")
    print(video_folder)

    # =====================================
    # TRANSCRIPT PATH
    # =====================================

    transcript_path = (
        f"{video_folder}/transcript.json"
    )

    # =====================================
    # LOAD TRANSCRIPT
    # =====================================

    with open(
        transcript_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    segments = data["segments"]

    # =====================================
    # CREATE CHUNKS
    # =====================================

    chunks = create_semantic_chunks(
        segments
    )

    # =====================================
    # OUTPUT PATH
    # =====================================

    output_path = (
        f"{video_folder}/semantic_chunks.json"
    )

    # =====================================
    # SAVE CHUNKS
    # =====================================

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            chunks,

            f,

            indent=4,

            ensure_ascii=False
        )

    # =====================================
    # DONE
    # =====================================

    print("\nTOTAL CHUNKS:")
    print(len(chunks))

    print("\nFIRST CHUNK:\n")

    print(
        json.dumps(

            chunks[0],

            indent=4,

            ensure_ascii=False
        )
    )