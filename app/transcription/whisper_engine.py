from faster_whisper import WhisperModel
import torch


class WhisperTranscriber:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.compute_type = (
            "float16"
            if self.device == "cuda"
            else "int8"
        )

        print(f"Using device: {self.device}")

        self.model = WhisperModel(
            "large-v3",
            device=self.device,
            compute_type=self.compute_type
        )

    def transcribe(self, audio_path):

        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            word_timestamps=True
        )

        transcript_segments = []

        for i, segment in enumerate(segments):

            transcript_segments.append({

                "segment_id": i,

                "start": round(segment.start, 2),

                "end": round(segment.end, 2),

                "text": segment.text.strip()
            })

        return transcript_segments