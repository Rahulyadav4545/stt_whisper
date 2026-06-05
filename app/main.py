import json

from transcription.whisper_engine import (
    WhisperTranscriber
)

from diarization.speaker_engine import (
    SpeakerDiarizer
)

from diarization.speaker_merger import (
    merge_transcript_and_speakers
)
from chunking.semantic_chunker import (
    create_semantic_chunks
)
# =========================================
# AUDIO PATH
# =========================================

audio_path = "/media/ori_quadro/newhd1/Rahul/data/joe_dispenza_sleep.mp3"

# =========================================
# WHISPER TRANSCRIPTION
# =========================================

print("\nStarting transcription...\n")

transcriber = WhisperTranscriber()

transcript_segments = transcriber.transcribe(
    audio_path
)

print("TRANSCRIPTION COMPLETED\n")

# =========================================
# SPEAKER DIARIZATION
# =========================================

print("Starting speaker diarization...\n")

diarizer = SpeakerDiarizer()

speaker_segments = diarizer.diarize(
    audio_path
)

print("DIARIZATION COMPLETED\n")

# =========================================
# MERGE SPEAKERS + TRANSCRIPT
# =========================================

print("Merging transcript with speakers...\n")

merged_output = merge_transcript_and_speakers(
    transcript_segments,
    speaker_segments
)

print("MERGING COMPLETED\n")

# =========================================
# CREATE SEMANTIC CHUNKS
# =========================================

print("Creating semantic chunks...\n")

semantic_chunks = create_semantic_chunks(
    merged_output
)

print("SEMANTIC CHUNKING COMPLETED\n")

# =========================================
# SAVE FINAL JSON
# =========================================

output_path = "backend/app/outputs/final_transcript.json"

with open(
    output_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
    semantic_chunks,
        f,
        indent=4,
        ensure_ascii=False
    )

print(f"Final transcript saved:\n{output_path}")