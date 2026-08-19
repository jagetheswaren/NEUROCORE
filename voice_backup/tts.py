import pyttsx3


class TextToSpeech:

    def __init__(self):
        self.engine = pyttsx3.init()

        self.engine.setProperty("rate", 185)
        self.engine.setProperty("volume", 1.0)

        self.voices = self.engine.getProperty("voices")

        self.english_voice = None
        self.tamil_voice = None

        for voice in self.voices:

            info = (
                str(voice.id) + " " +
                str(getattr(voice, "name", "")) + " " +
                str(getattr(voice, "languages", ""))
            ).lower()

            if (
                "tamil" in info
                or "ta-in" in info
                or "tamil india" in info
            ):
                self.tamil_voice = voice.id

            if (
                "english" in info
                or "en-in" in info
                or "en-us" in info
            ):
                if self.english_voice is None:
                    self.english_voice = voice.id

    def _is_tamil(self, text):

        tamil_chars = 0
        total_chars = 0

        for char in text:

            if char.isspace():
                continue

            total_chars += 1

            if "\u0B80" <= char <= "\u0BFF":
                tamil_chars += 1

        if total_chars == 0:
            return False

        return (tamil_chars / total_chars) > 0.15

    def speak(self, text):

        if self._is_tamil(text):

            if self.tamil_voice:
                self.engine.setProperty(
                    "voice",
                    self.tamil_voice
                )

        else:

            if self.english_voice:
                self.engine.setProperty(
                    "voice",
                    self.english_voice
                )

        self.engine.say(text)
        self.engine.runAndWait()