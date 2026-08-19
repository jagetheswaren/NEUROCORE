import sys
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()
SERVER_URL = "http://127.0.0.1:8000"

class ThinNeuroCoreCLI:
    def __init__(self):
        self.current_mode = "friend"
        self.check_server()

    def check_server(self):
        try:
            r = requests.get(f"{SERVER_URL}/health", timeout=3)
            if r.status_code == 200:
                data = r.json()
                console.print(f"[bold green]Connected to NEUROCORE Core API[/bold green] (v{data.get('version')})")
            else:
                console.print(f"[bold yellow]Server warning: HTTP {r.status_code}[/bold yellow]")
        except Exception:
            console.print("[bold red]Error: NEUROCORE API Server not running at http://127.0.0.1:8000[/bold red]")
            console.print("[dim]Start the server with: python server/app.py[/dim]\n")

    def show_banner(self):
        console.print(Panel.fit(
            "[bold cyan]🧠 NEUROCORE THIN CLI CLIENT (v0.5)[/bold cyan]\n"
            "[dim]Connected via FastAPI Gateway to Central Core[/dim]",
            border_style="cyan"
        ))

    def run(self):
        self.show_banner()
        while True:
            try:
                user_input = console.input(f"\n[bold magenta]NEUROCORE ({self.current_mode}) > [/bold magenta]").strip()
                if not user_input:
                    continue

                if user_input in {"exit", "quit"}:
                    console.print("[bold cyan]Goodbye![/bold cyan]")
                    break

                if user_input.startswith("/mode"):
                    parts = user_input.split()
                    if len(parts) > 1:
                        self.current_mode = parts[1]
                        console.print(f"[green]Switched mode to: {self.current_mode}[/green]")
                    else:
                        console.print(f"[yellow]Current mode: {self.current_mode}[/yellow]")
                    continue

                if user_input == "/memory":
                    r = requests.get(f"{SERVER_URL}/memory")
                    if r.status_code == 200:
                        mems = r.json().get("memories", [])
                        table = Table(title="NEUROCORE Stored Memories")
                        table.add_column("ID", style="cyan")
                        table.add_column("Content", style="white")
                        table.add_column("Category", style="green")
                        for m in mems:
                            table.add_row(str(m["id"]), m["content"], m["category"])
                        console.print(table)
                    continue

                if user_input.startswith("/remember"):
                    content = user_input[len("/remember"):].strip()
                    r = requests.post(f"{SERVER_URL}/memory", json={"content": content})
                    if r.status_code == 200:
                        console.print("[bold green]Memory saved successfully via API.[/bold green]")
                    continue

                # Normal chat request to FastAPI Core Gateway
                payload = {"message": user_input, "mode": self.current_mode}
                res = requests.post(f"{SERVER_URL}/chat", json=payload, timeout=120)
                
                if res.status_code == 200:
                    data = res.json()
                    console.print(Panel(data["response"], title=f"AI ({data['mode']} | {data['tier']})", border_style="green"))
                else:
                    console.print(f"[bold red]API Error ({res.status_code}): {res.text}[/bold red]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted.[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Client Error: {e}[/bold red]")

if __name__ == "__main__":
    cli = ThinNeuroCoreCLI()
    cli.run()
