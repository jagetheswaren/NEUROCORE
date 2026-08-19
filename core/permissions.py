class PermissionManager:

    def __init__(self, config):
        self.safe = config.get("safe", config.get("auto_approve", []))
        self.auto_approve = config.get("auto_approve", self.safe)
        self.ask = config.get("ask", [])
        self.sensitive = config.get("sensitive", [])
        self.blocked = config.get("blocked", ["format", "shutdown", "restart", "reg delete", "net user", "drop database"])

    def check(self, mode_or_command, command=None):
        cmd = command if command is not None else mode_or_command
        return self.status(cmd)

    def status(self, command):
        if not command or not command.strip():
            return "ask"
        lower = command.strip().lower()

        for pattern in self.blocked:
            if pattern in lower:
                return "blocked"

        for pattern in self.sensitive:
            if pattern in lower:
                return "sensitive"

        for pattern in self.auto_approve:
            if lower == pattern or lower.startswith(pattern + " "):
                return "auto"

        for pattern in self.safe:
            if lower == pattern or lower.startswith(pattern + " "):
                return "safe"

        return "ask"

    def request(self, command, interactive=True):
        st = self.status(command)

        if st == "blocked":
            return False, "blocked by security policy"

        if st in {"auto", "safe"}:
            return True, "auto-approved"

        if not interactive:
            return False, f"requires approval ({st})"

        label = "SENSITIVE" if st == "sensitive" else "RUN"

        answer = input(
            f"\n[{label}] Execute: {command}? [y/N] "
        ).strip().lower()

        if answer in {"y", "yes"}:
            return True, "approved"

        return False, "denied"