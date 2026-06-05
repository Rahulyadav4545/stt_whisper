from pyannote.audio import Pipeline
import torch


class SpeakerDiarizer:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(f"Using device: {self.device}")

        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1"
        )

        self.pipeline.to(torch.device(self.device))

    def diarize(self, audio_path):

        diarization = self.pipeline(audio_path)

        speaker_segments = []

        for turn, _, speaker in diarization.itertracks(
            yield_label=True
        ):

            speaker_segments.append({

                "speaker": speaker,

                "start": round(turn.start, 2),

                "end": round(turn.end, 2)
            })

        return speaker_segments
        # return diarizat
        