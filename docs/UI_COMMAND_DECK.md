# Command Deck UI

The Command Deck is the opt-in V0.2 workspace layered on top of the stable V0.1 HUD.

## Layout

```text
Rail | Context Header
     | Main Screen Canvas | Activity / Inspector
     | Command Input
```

## Screens

- Dashboard — system and mission overview.
- Chat — conversation stream.
- Agents — registry and capability status.
- Tasks — shared task lifecycle.
- Voice — provider status and future Language Lab.
- Projects — project context.
- Memory — persistent context.
- Settings — runtime preferences.

## Design principles

- Dark graphite surfaces with cyan, violet, amber, green, and red state tokens.
- Reduced motion is respected.
- ASCII-safe labels remain available for Windows terminals.
- Narrow widths collapse the rail and inspector without losing input or approval controls.
- The same screen registry drives navigation and command-palette behavior.
- Empty, unavailable, and failed states are explicit.

Enable with:

```json
"v02_ui_enabled": true
```

The default remains `false`.

