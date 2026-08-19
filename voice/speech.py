import logging
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from pathlib import Path


logger = logging.getLogger(__name__)


class SpeechRecognizer:

    def __init__(self):
        """Initialize speech recognizer with error handling."""
        logger.info("Loading speech recognition model...")
        print("Loading speech recognition model...")

        try:
            self.model = WhisperModel(
                "small",
                device="cpu",
                compute_type="int8"
            )
            logger.info("Speech recognition model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load speech model: {str(e)}")
            raise

        self.audio_file = Path("voice") / "input.wav"
        self.sample_rate = 16000

    def listen(
        self,
        max_seconds=15,
        silence_seconds=0.9,
        threshold=350
    ):
        """Listen for audio input with error handling."""
        chunk_seconds = 0.2
        chunk_frames = int(self.sample_rate * chunk_seconds)

        print("\n🎙 Listening... Speak now.")
        logger.info(f"Starting audio capture (max {max_seconds}s)")

        try:
            # Check if audio device is available
            devices = sd.query_devices()
            if devices is None or len(devices) == 0:
                error_msg = "No audio input device found"
                logger.error(error_msg)
                print(f"[error] {error_msg}")
                return ""

        except Exception as e:
            error_msg = f"Failed to query audio devices: {str(e)}"
            logger.error(error_msg)
            print(f"[error] {error_msg}")
            return ""

        audio = []
        speech_started = False
        silence_frames = 0

        try:
            for i in range(int(max_seconds / chunk_seconds)):

                try:
                    block = sd.rec(
                        chunk_frames,
                        samplerate=self.sample_rate,
                        channels=1,
                        dtype="int16"
                    )

                    sd.wait()

                except Exception as e:
                    error_msg = f"Audio capture failed: {str(e)}"
                    logger.error(error_msg)
                    print(f"[error] {error_msg}")
                    if audio:
                        break  # Use what we have so far
                    else:
                        return ""

                energy = (
                    block.astype("float32") ** 2
                ).mean()

                if energy > threshold:

                    if not speech_started:
                        speech_started = True
                        logger.debug("Speech detected")

                    silence_frames = 0
                    audio.append(block)

                elif speech_started:

                    silence_frames += 1
                    audio.append(block)

                    if silence_frames >= int(
                        silence_seconds / chunk_seconds
                    ):
                        logger.debug("Silence detected, stopping capture")
                        break

            if not speech_started:
                logger.warning("No speech detected during listen")
                print("...no speech detected.")
                return ""

            full_audio = np.concatenate(audio)

            try:
                wav.write(
                    self.audio_file,
                    self.sample_rate,
                    full_audio
                )
                logger.debug(f"Audio saved to {self.audio_file}")
            except Exception as e:
                error_msg = f"Failed to save audio file: {str(e)}"
                logger.error(error_msg)
                print(f"[error] {error_msg}")
                return ""

            print("🧠 Understanding...")
            logger.info("Starting transcription")

            try:
                segments, info = self.model.transcribe(
                    str(self.audio_file),
                    beam_size=3,
                    vad_filter=True,
                    condition_on_previous_text=False
                )

                text = " ".join(
                    segment.text.strip()
                    for segment in segments
                )

                logger.info(f"Transcription complete: '{text[:50]}...'")
                return text.strip()

            except Exception as e:
                error_msg = f"Transcription failed: {str(e)}"
                logger.error(error_msg)
                print(f"[error] {error_msg}")
                return ""

        except Exception as e:
            error_msg = f"Unexpected error during listen: {str(e)}"
            logger.exception(error_msg)
            print(f"[error] {error_msg}")
            return ""