# Voice and Language

Voice is optional and must never be required for text mode or normal TUI startup.

## Existing direction

- `voice/speech.py` contains the optional speech recognition path.
- `voice/tts.py` contains the optional text-to-speech path.
- `requirements-voice.txt` contains optional audio dependencies.
- Imports are lazy so missing audio packages do not break the base application.

## Planned provider boundary

```text
Voice Agent
  -> Speech-to-Text Provider
  -> NEUROCORE
  -> Text-to-Speech Provider
```

The future provider contract should expose capability and availability status, transcription, synthesis, language detection, and explicit failure states.

## Language Lab

The planned Language Lab includes target language, level, lessons, listening, speaking practice, pronunciation, conversation, quizzes, and progress. It must report actual provider support instead of claiming every language is available.

Voice remains disabled or `NOT CONFIGURED` until a provider, device, and model are available.

