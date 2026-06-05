from pathlib import Path
import json

from faster_whisper import WhisperModel

# =====================================
# LOAD MODEL
# =====================================

model = WhisperModel(
    "medium",
    device="cuda",
    compute_type="float16"
)

# =====================================
# RUN TRANSCRIPTION
# =====================================

def run_transcription(video_path):

    print("\nRUNNING TRANSCRIPTION\n")

    video_path = Path(video_path)

    # =====================================
    # OUTPUT FOLDER
    # =====================================

    output_folder = Path(
        "/media/ori_quadro/newhd1/Rahul/storage/outputs"
    ) / video_path.stem

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # =====================================
    # TRANSCRIBE
    # =====================================

    segments_generator, info = model.transcribe(
        str(video_path)
    )

    segments = []

    full_text = []

    for idx, segment in enumerate(segments_generator):

        segments.append({

            "chunk_id": idx,

            "text": segment.text,

            "start": segment.start,

            "end": segment.end
        })

        full_text.append(
            segment.text
        )

    # =====================================
    # SAVE JSON
    # =====================================

    json_path = (
        output_folder / "transcript.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            {
                "segments": segments
            },
            f,
            indent=4,
            ensure_ascii=False
        )

    # =====================================
    # SAVE TXT
    # =====================================

    txt_path = (
        output_folder / "transcript.txt"
    )

    with open(
        txt_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(full_text)
        )

    print("\nTRANSCRIPTION COMPLETED\n")

    return str(output_folder)