"""Visual tokens for the opt-in V0.2 Command Deck workspace."""

BACKGROUND = "#081018"
SURFACE = "#0d1a25"
SURFACE_RAISED = "#122535"
LINE = "#1e4658"
TEXT = "#d7f9ff"
MUTED = "#7895a3"
CYAN = "#00d9ff"
VIOLET = "#d68cff"
GREEN = "#42f58d"
AMBER = "#ffd166"
RED = "#ff6b7a"

WORKSPACE_CSS = f"""
Screen {{
    background: {BACKGROUND};
    color: {TEXT};
}}
#deck {{ height: 1fr; }}
#rail {{
    width: 20;
    background: {SURFACE};
    border-right: solid {LINE};
    padding: 1;
}}
#rail-title {{ color: {CYAN}; text-style: bold; padding-bottom: 1; }}
#rail-subtitle {{ color: {MUTED}; padding-bottom: 1; }}
#rail Button {{
    width: 100%;
    min-width: 0;
    margin: 0 0 1 0;
    background: transparent;
    color: {MUTED};
    border: none;
    content-align: left middle;
}}
#rail Button:hover, #rail Button.-active {{
    color: {TEXT};
    background: {SURFACE_RAISED};
}}
#workspace {{ width: 1fr; }}
#context {{
    height: 5;
    background: {SURFACE};
    border-bottom: solid {LINE};
    padding: 1 2;
}}
#context-title {{ color: {CYAN}; text-style: bold; }}
#context-meta {{ color: {MUTED}; }}
#canvas {{ height: 1fr; padding: 1 2; }}
#canvas-title {{ color: {VIOLET}; text-style: bold; }}
#canvas-body {{ color: {TEXT}; padding-top: 1; }}
#inspector {{
    width: 29;
    background: {SURFACE};
    border-left: solid {LINE};
    padding: 1;
}}
#inspector-title {{ color: {CYAN}; text-style: bold; }}
#inspector-body {{ color: {MUTED}; padding-top: 1; }}
#command {{
    dock: bottom;
    margin: 1 2;
    border: round {CYAN};
}}
.state {{ color: {GREEN}; }}
.muted {{ color: {MUTED}; }}
.approval {{ color: {AMBER}; }}
.danger {{ color: {RED}; }}
"""
