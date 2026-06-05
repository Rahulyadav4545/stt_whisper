def merge_transcript_and_speakers(
    transcript_segments,
    speaker_segments
):

    merged_output = []

    for segment in transcript_segments:

        segment_start = segment["start"]
        segment_end = segment["end"]

        best_speaker = "UNKNOWN"
        best_overlap = 0

        for speaker_turn in speaker_segments:

            overlap_start = max(
                segment_start,
                speaker_turn["start"]
            )

            overlap_end = min(
                segment_end,
                speaker_turn["end"]
            )

            overlap = max(
                0,
                overlap_end - overlap_start
            )

            if overlap > best_overlap:

                best_overlap = overlap

                best_speaker = speaker_turn["speaker"]

        merged_output.append({

            "speaker": best_speaker,

            "start": segment_start,

            "end": segment_end,

            "text": segment["text"]
        })

    return merged_output