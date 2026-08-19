import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from pathlib import Path


class SpeechRecognizer:

    def __init__(self):
        print("Loading speech recognition model...")

        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

        self.audio_file = Path("voice") / "input.wav"

    def listen(self, seconds=6):

        print("\n🎙 Listening... Speak now.")

        sample_rate = 16000

        audio = sd.rec(
            int(seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        wav.write(
            self.audio_file,
            sample_rate,
            audio
        )

        print("🧠 Understanding...")

        segments, info = self.model.transcribe(
            str(self.audio_file),
            beam_size=5
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return text.strip()