from rich.console import Console
from rich.panel import Panel

from core.brain import NeuroCore
from voice.speech import SpeechRecognizer
from voice.tts import TextToSpeech


console = Console()

brain = NeuroCore()
speech = None
tts = None


def initialize_voice():
    global speech, tts

    if speech is None:
        speech = SpeechRecognizer()

    if tts is None:
        tts = TextToSpeech()


def voice_mode():
    initialize_voice()

    console.print(
        "\n[bold cyan]🎙 NEUROCORE Voice Mode[/bold cyan]"
    )

    console.print(
        "[yellow]Say 'stop voice mode' or 'குரல் நிறுத்து' to return.[/yellow]"
    )

    while True:

        try:
            text = speech.listen()

            if not text:
                console.print(
                    "[yellow]I didn't hear anything.[/yellow]"
                )
                continue

            text = text.strip()

            console.print(
                f"\n[bold green]You > [/bold green]{text}"
            )

            # Convert command to lowercase
            lower_text = text.lower().strip()

            # Voice exit commands
            stop_commands = [
                "stop voice mode",
                "exit voice mode",
                "voice off",
                "turn off voice",
                "stop listening",
                "stop voice",

                # Tamil
                "குரல் நிறுத்து",
                "குரல் நிறுத்துங்கள்",
                "வாய்ஸ் ஆஃப்",
                "வாய்ஸ் நிறுத்து",
                "வாய்ஸ் மோட் ஆஃப்",
                "வாய்ஸ் மோட் நிறுத்து",
            ]

            # Check whether user wants to exit voice mode
            if any(command in lower_text for command in stop_commands):

                console.print(
                    "\n[yellow]🔇 Voice mode stopped.[/yellow]"
                )

                tts.speak(
                    "Voice mode stopped. "
                    "குரல் பயன்முறை நிறுத்தப்பட்டது."
                )

                break

            # Send normal message to AI
            answer = brain.ask(text)

            console.print(
                f"\n[bold cyan]NEUROCORE > [/bold cyan]{answer}"
            )

            # Speak AI response
            tts.speak(answer)

        except KeyboardInterrupt:

            console.print(
                "\n[yellow]🔇 Voice mode stopped.[/yellow]"
            )

            break

        except Exception as error:

            console.print(
                f"[bold red]Voice Error:[/bold red] {error}"
            )


def main():

    console.print(
        Panel.fit(
            "[bold cyan]NEUROCORE v0.3[/bold cyan]\n"
            "Local AI Brain + Memory + Voice\n"
            "Model: Qwen3 8B\n\n"
            "Commands:\n"
            "/remember <information>\n"
            "/memory\n"
            "/voice\n"
            "exit",
            title="NEUROCORE"
        )
    )

    while True:

        try:

            message = console.input(
                "\n[bold green]You > [/bold green]"
            )

            message = message.strip()

            # Normal CLI exit
            if message.lower() in {"exit", "quit"}:

                console.print(
                    "[yellow]NEUROCORE shutting down.[/yellow]"
                )

                break

            # Voice mode
            if message.lower() == "/voice":

                voice_mode()
                continue

            # Remember
            if message.startswith("/remember "):

                information = message[
                    len("/remember "):
                ].strip()

                if information:

                    result = brain.remember(
                        information
                    )

                    console.print(
                        f"[bold cyan]NEUROCORE > [/bold cyan]"
                        f"{result}"
                    )

                continue

            # Memory
            if message.lower() == "/memory":

                memories = brain.memory.get_all()

                if not memories:

                    console.print(
                        "[yellow]No memories stored.[/yellow]"
                    )

                else:

                    console.print(
                        "\n[bold cyan]Long-term memory:[/bold cyan]"
                    )

                    for memory in memories:

                        console.print(
                            f"[green]•[/green] {memory[1]}"
                        )

                continue

            # Ignore empty input
            if not message:
                continue

            # Normal AI chat
            console.print(
                "\n[bold cyan]NEUROCORE > [/bold cyan]"
            )

            answer = brain.ask(message)

            console.print(answer)

        except KeyboardInterrupt:

            console.print(
                "\n[yellow]NEUROCORE stopped.[/yellow]"
            )

            break

        except Exception as error:

            console.print(
                f"[bold red]Error:[/bold red] {error}"
            )


if __name__ == "__main__":
    main()