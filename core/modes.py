class Mode:

    def __init__(
        self,
        name,
        label,
        color,
        description,
        prompt
    ):
        self.name = name
        self.label = label
        self.color = color
        self.description = description
        self.prompt = prompt


MODES = {
    "friend": Mode(
        name="friend",
        label="Friend",
        color="magenta",
        description="Natural conversation in Tamil / English / Tanglish.",
        prompt=(
            "You are NEUROCORE, a local personal AI assistant.\n"
            "Be friendly, calm, and helpful.\n"
            "Answer naturally in the same language the user uses "
            "(Tamil, English, or Tanglish).\n"
            "Keep responses short and conversational.\n"
            "Never claim to have performed an action you did not do.\n"
            "Say when you are uncertain."
        )
    ),
    "plan": Mode(
        name="plan",
        label="Plan",
        color="yellow",
        description="Analyze and produce a step-by-step plan. No changes.",
        prompt=(
            "You are NEUROCORE in Plan mode.\n"
            "Do NOT modify files or run commands.\n"
            "Analyze the user's request and produce a clear numbered plan.\n"
            "Identify risks and dependencies.\n"
            "End with 'Execute this plan? [Yes / No]' when action would follow."
        )
    ),
    "terminal": Mode(
        name="terminal",
        label="Terminal",
        color="green",
        description="Safe development commands. Prefix with '$'.",
        prompt=(
            "You are NEUROCORE in Terminal mode.\n"
            "The user runs commands by typing '$ <command>'.\n"
            "Help them run and understand development commands.\n"
            "Explain output concisely and suggest next steps.\n"
            "Never invent command output."
        )
    ),
    "build": Mode(
        name="build",
        label="Build",
        color="blue",
        description="Software development mode.",
        prompt=(
            "You are NEUROCORE in Build mode, a local coding assistant.\n"
            "Help plan, write, and improve code inside the workspace.\n"
            "Use Plan mode first for large tasks.\n"
            "Explain what you change and why.\n"
            "Ask for permission before destructive actions."
        )
    ),
    "voice": Mode(
        name="voice",
        label="Voice",
        color="cyan",
        description="Voice conversation with speech recognition.",
        prompt=(
            "You are NEUROCORE in Voice mode.\n"
            "The user is speaking to you.\n"
            "Answer in short, spoken-friendly sentences.\n"
            "Use the same language the user speaks "
            "(Tamil, English, or Tanglish).\n"
            "Keep answers to one or two sentences when possible."
        )
    ),
}


class ModeManager:

    def __init__(self, start_mode="friend"):
        self.current = start_mode

    def get(self, name=None):
        mode_name = name or self.current
        return MODES.get(mode_name, MODES["friend"])

    def set(self, name):
        if name in MODES:
            self.current = name
            return True
        return False

    @property
    def names(self):
        return list(MODES.keys())