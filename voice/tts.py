import logging
import os
import sys
import subprocess
import tempfile
import winsound


logger = logging.getLogger(__name__)


class TextToSpeech:

    def __init__(self):
        """Initialize TextToSpeech with model validation and error handling."""

        # ==========================================
        # TAMIL PIPER MODEL
        # ==========================================

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.model = os.path.join(
            base_dir,
            "models",
            "ta_IN-rasa_female-medium.onnx"
        )

        self.config = os.path.join(
            base_dir,
            "models",
            "ta_IN-rasa_female-medium.onnx.json"
        )

        # ==========================================
        # VERIFY MODEL
        # ==========================================

        try:
            if not os.path.isfile(self.model):
                error_msg = f"Tamil Piper model not found: {self.model}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            if not os.path.isfile(self.config):
                error_msg = f"Tamil Piper configuration not found: {self.config}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            logger.info("TextToSpeech initialized successfully")

        except FileNotFoundError as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    # ==========================================
    # CHECK WHETHER TEXT CONTAINS TAMIL
    # ==========================================

    def is_tamil(self, text):
        """Check if text contains at least 10% Tamil characters."""

        tamil_count = 0
        letter_count = 0

        for char in text:

            if char.isspace():
                continue

            if char.isalpha():

                letter_count += 1

                if "\u0B80" <= char <= "\u0BFF":
                    tamil_count += 1

        if letter_count == 0:
            return False

        return (
            tamil_count / letter_count
        ) >= 0.10

    # ==========================================
    # SPEAK
    # ==========================================

    def speak(self, text):
        """Convert text to speech with error handling and logging."""

        if text is None:
            logger.debug("speak() called with None text, returning")
            return

        text = str(text).strip()

        if not text:
            logger.debug("speak() called with empty text, returning")
            return

        # ======================================
        # CURRENTLY PIPER IS TAMIL VOICE
        # ======================================

        if not self.is_tamil(text):
            logger.info(f"Non-Tamil response detected, text output only: {text[:50]}...")
            print("[TTS] Non-Tamil response:")
            print(text)
            return

        # ======================================
        # TEMPORARY WAV FILE
        # ======================================

        wav_file = os.path.join(
            tempfile.gettempdir(),
            "neurocore_tts.wav"
        )

        try:

            # ==================================
            # PIPER COMMAND
            # ==================================

            command = [
                sys.executable,
                "-m",
                "piper",

                "-m",
                self.model,

                "-c",
                self.config,

                "-f",
                wav_file,

                "--sentence-silence",
                "0",

                "--volume",
                "1.0"
            ]

            logger.debug(f"Generating speech for Tamil text (length: {len(text)})")

            # ==================================
            # GENERATE SPEECH
            # ==================================

            try:
                process = subprocess.run(
                    command,

                    input=text,

                    text=True,

                    capture_output=True,

                    encoding="utf-8",

                    errors="replace",

                    timeout=30
                )

            except subprocess.TimeoutExpired:
                error_msg = "Piper TTS generation timed out after 30s"
                logger.error(error_msg)
                print(f"\n[TTS ERROR] {error_msg}")
                return

            except FileNotFoundError:
                error_msg = "Piper is not installed. Install with: pip install piper-tts"
                logger.error(error_msg)
                print(f"\n[TTS ERROR] {error_msg}")
                return

            # ==================================
            # PIPER ERROR
            # ==================================

            if process.returncode != 0:
                error_msg = f"Piper TTS failed with exit code {process.returncode}"
                logger.error(f"{error_msg}: {process.stderr}")
                print("\n[TTS ERROR]")
                print(process.stderr)
                return

            # ==================================
            # PLAY AUDIO
            # ==================================

            if not os.path.exists(wav_file):
                error_msg = "TTS WAV file was not created by Piper"
                logger.error(error_msg)
                print(f"[TTS ERROR] {error_msg}")
                return

            try:
                logger.debug(f"Playing audio file: {wav_file}")
                winsound.PlaySound(
                    wav_file,
                    winsound.SND_FILENAME
                )
                logger.info("Audio playback completed successfully")

            except Exception as e:
                error_msg = f"Failed to play audio: {str(e)}"
                logger.error(error_msg)
                print(f"\n[TTS ERROR] {error_msg}")
                return

        except FileNotFoundError as error:
            error_msg = "Piper could not be started"
            logger.error(f"{error_msg}: {str(error)}")
            print(f"\n[TTS ERROR] {error_msg}")
            print(error)

        except Exception as error:
            error_msg = f"Unexpected error during TTS: {str(error)}"
            logger.exception(error_msg)
            print("\n[TTS ERROR]")
            print(error)

        finally:

            # ==================================
            # CLEAN TEMP AUDIO
            # ==================================

            try:

                if os.path.exists(wav_file):
                    os.remove(wav_file)
                    logger.debug("Cleaned up temporary audio file")

            except Exception as e:
                logger.warning(f"Failed to clean up temporary audio file: {str(e)}")
                pass