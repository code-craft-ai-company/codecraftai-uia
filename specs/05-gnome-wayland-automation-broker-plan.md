# Option A Implementation Plan (Deeper) — GNOME Wayland (Ubuntu 24.04) Automation Introspection Broker

This document specifies a concrete “Option A” implementation: a **GNOME Shell extension** (running inside GNOME Shell / Mutter) that exposes **window + display geometry** via a **local-only IPC endpoint**, enabled **only while a user-started service is running**. When the service stops, the capability vanishes (socket removed; server stopped).

Target environment:
- **Ubuntu 24.04**
- **GNOME on Wayland** (Mutter compositor / GNOME Shell)
- Typical GNOME version family: **GNOME 46.x**

---

## 1. Desired behavior (capability lifecycle)

### Start
1. User runs: `automation-broker start` (or `systemctl --user start automation-broker`)
2. The service:
   - creates a token file in `$XDG_RUNTIME_DIR`
   - enables the GNOME Shell extension (if not already enabled)
3. The extension detects the token file (“armed”), starts the IPC server, and creates:
   - socket: `$XDG_RUNTIME_DIR/automation-broker.sock`
4. Clients connect using the token and query:
   - outputs/monitors, scaling
   - windows + global geometry
   - (optional) subscribe to changes

### Stop
1. User runs: `automation-broker stop` (or `systemctl --user stop automation-broker`)
2. The service:
   - disables the extension (or deletes token file; either is sufficient)
   - removes token file
3. The extension immediately:
   - stops IPC server
   - removes socket file  
4. Clients lose access (socket gone).

---

## 2. High-level architecture

### Components
- **GNOME Shell Extension** (JS):
  - Trusted access to window tree and monitor layout
  - Implements a small IPC server (Unix socket)
  - Serves JSON-RPC-like requests
  - Optional event stream
- **User service** (systemd `--user`):
  - Generates token
  - Enables/disables the extension
  - Cleans up artifacts on stop
- **CLI**:
  - Convenience wrapper around systemd + optional debug commands
- **Client library**:
  - Python helper for connecting and consuming data

### Transport: Unix domain socket (recommended)
- Socket: `$XDG_RUNTIME_DIR/automation-broker.sock`
- Permissions: `0600` (only the user can connect)
- Token: `$XDG_RUNTIME_DIR/automation-broker.token` with `0600`

---

## 3. Files and directory layout

### Extension install location (per-user)
```
~/.local/share/gnome-shell/extensions/
  com.yourorg.automationbroker@yourorg/
    metadata.json
    extension.js
    stylesheet.css            (optional)
    schemas/                  (optional if you add GSettings)
    README.md                 (optional)
```

### Broker runtime artifacts (per-session)
```
$XDG_RUNTIME_DIR/
  automation-broker.sock
  automation-broker.token
```

### User service + CLI
```
~/.config/systemd/user/automation-broker.service
~/.local/bin/automation-broker
```

---

## 4. API definition (JSON over socket)

### Message framing
- Newline-delimited JSON (NDJSON):
  - one JSON object per line
  - responses are one line each
  - event stream is additional lines

### Request envelope
```json
{"id": 1, "method": "ListOutputs", "params": {"token": "…"}}
```

### Response envelope
```json
{"id": 1, "ok": true, "result": {...}}
```

### Error envelope
```json
{"id": 1, "ok": false, "error": {"code": "UNAUTHORIZED", "message": "Invalid token"}}
```

### Methods (v1)
- `GetVersion() -> { api_version, gnome_version }`
- `ListOutputs() -> [Output]`
- `ListWorkspaces() -> [Workspace]`
- `ListWindows(filters?) -> [Window]`
- `GetWindow({window_id}) -> Window`
- `WindowAt({x,y,space="logical"}) -> {window_id|null, local_x, local_y}`
- `ConvertPoint({x,y,from_space,to_space,output_id?}) -> {x,y}`
- `Subscribe({events:[...], token}) -> stream of Event messages` *(optional milestone)*

### Data types

#### Output
```json
{
  "id": "mon-0",
  "name": "HDMI-1",
  "primary": true,
  "logical_rect": {"x": 0, "y": 0, "w": 1920, "h": 1080},
  "physical_rect": {"x": 0, "y": 0, "w": 1920, "h": 1080},
  "scale": 1.0,
  "transform": "normal",
  "refresh_hz": 60.0
}
```

#### Window
```json
{
  "id": "win-42",
  "app_id": "org.gnome.Terminal",
  "title": "Terminal",
  "focused": false,
  "workspace": 1,
  "output_id": "mon-0",
  "rect_logical": {"x": 40, "y": 60, "w": 900, "h": 700},
  "rect_physical": {"x": 40, "y": 60, "w": 900, "h": 700}
}
```

**Rect meanings**
- Prefer **frame rect** (window frame/borders) as `rect_*` because automation needs where the window is on screen.
- If you also want client content area, expose `content_rect_*` later.

---

## 5. Security and gating model

### Baseline
- Only accessible to same user (socket in `$XDG_RUNTIME_DIR`, mode `0600`).

### “Armed only when service is running”
- The extension should run its server *only if* `$XDG_RUNTIME_DIR/automation-broker.token` exists.
- Token file acts as:
  - **arming signal**
  - **authentication secret**

### Token validation
- On each request:
  - check `params.token` equals contents of token file
  - allow `GetVersion()` without token for easier health checks (optional)

---

## 6. GNOME Shell extension details

### 6.1 `metadata.json` (example)
```json
{
  "uuid": "com.yourorg.automationbroker@yourorg",
  "name": "Automation Broker",
  "description": "Exposes window + display geometry via a gated local socket for automation.",
  "shell-version": ["46"],
  "version": 1
}
```

> Note: you may add additional `shell-version` entries after testing on minor updates (e.g., 46.1, 46.2). GNOME Extensions usually matches major version.

---

## 7. Extension implementation skeleton (JS)

> This is a **skeleton** to illustrate structure. Expect you’ll refine imports and signal handling for GNOME 46 APIs.

### 7.1 Imports & constants
```js
// extension.js
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const API_VERSION = "1.0";
const TOKEN_FILE = "automation-broker.token";
const SOCK_FILE  = "automation-broker.sock";
```

### 7.2 Helper: runtime paths
```js
function runtimeDir() {
  // Usually /run/user/<uid>
  return GLib.getenv('XDG_RUNTIME_DIR');
}

function tokenPath() {
  return GLib.build_filenamev([runtimeDir(), TOKEN_FILE]);
}

function sockPath() {
  return GLib.build_filenamev([runtimeDir(), SOCK_FILE]);
}
```

### 7.3 Helper: token read
```js
function readToken() {
  const path = tokenPath();
  const file = Gio.File.new_for_path(path);
  if (!file.query_exists(null)) return null;

  const [ok, contents] = file.load_contents(null);
  if (!ok) return null;
  return (new TextDecoder()).decode(contents).trim();
}
```

### 7.4 Output enumeration (monitors)
GNOME Shell provides monitor info through `Main.layoutManager` and/or `global.display`. You’ll likely want:
- logical monitor rects (layout coordinates)
- scale factors

Skeleton approach:
```js
function listOutputs() {
  // Main.layoutManager.monitors is often easiest for logical geometry.
  // Each monitor object typically includes x, y, width, height.
  const monitors = Main.layoutManager.monitors || [];
  const primaryIndex = Main.layoutManager.primaryIndex ?? 0;

  return monitors.map((m, idx) => {
    // scale: can be global or per-monitor depending on fractional scaling
    // Some environments expose monitor.scale or global.display.get_monitor_scale(idx)
    const scale = (m.scale !== undefined) ? m.scale : 1.0;

    const logical = {x: m.x, y: m.y, w: m.width, h: m.height};

    // Physical rect: if scale is 2.0, physical pixels are logical*scale (approx)
    // Fractional scaling may require more careful mapping; expose scale and do best-effort.
    const physical = {
      x: Math.round(m.x * scale),
      y: Math.round(m.y * scale),
      w: Math.round(m.width * scale),
      h: Math.round(m.height * scale),
    };

    return {
      id: `mon-${idx}`,
      name: m.connector ?? m.name ?? `monitor-${idx}`,
      primary: idx === primaryIndex,
      logical_rect: logical,
      physical_rect: physical,
      scale: scale,
      transform: "normal",
      refresh_hz: m.refreshRate ?? null
    };
  });
}
```

---

### 7.5 Window enumeration
Most reliable enumeration in GNOME Shell:
- `global.get_window_actors()` and each actor’s `meta_window`.

Skeleton:
```js
function windowToObject(metaWindow, outputs) {
  const title = metaWindow.get_title?.() ?? "";
  const appId = metaWindow.get_gtk_application_id?.()
    ?? metaWindow.get_wm_class?.()
    ?? metaWindow.get_wm_class_instance?.()
    ?? null;

  const rect = metaWindow.get_frame_rect?.() ?? metaWindow.get_outer_rect?.();
  const rectLogical = {x: rect.x, y: rect.y, w: rect.width, h: rect.height};

  // Map to output by window center:
  const cx = rect.x + Math.floor(rect.width / 2);
  const cy = rect.y + Math.floor(rect.height / 2);

  let outputId = null;
  let scale = 1.0;
  for (const o of outputs) {
    const r = o.logical_rect;
    const inside = (cx >= r.x && cx < r.x + r.w && cy >= r.y && cy < r.y + r.h);
    if (inside) { outputId = o.id; scale = o.scale; break; }
  }

  const rectPhysical = {
    x: Math.round(rectLogical.x * scale),
    y: Math.round(rectLogical.y * scale),
    w: Math.round(rectLogical.w * scale),
    h: Math.round(rectLogical.h * scale)
  };

  const ws = metaWindow.get_workspace?.();
  const wsIndex = ws ? ws.index() : null;

  return {
    id: `win-${metaWindow.get_id?.() ?? metaWindow.toString()}`,
    app_id: appId,
    title: title,
    focused: metaWindow.has_focus?.() ?? false,
    workspace: wsIndex,
    output_id: outputId,
    rect_logical: rectLogical,
    rect_physical: rectPhysical
  };
}

function listWindows() {
  const outputs = listOutputs();
  const actors = global.get_window_actors?.() ?? [];
  const windows = [];

  for (const a of actors) {
    const mw = a.meta_window;
    if (!mw) continue;

    try {
      windows.push(windowToObject(mw, outputs));
    } catch (e) {
      // Defensive: avoid crashing shell
      log(`AutomationBroker: window enumeration error: ${e}`);
    }
  }

  return windows;
}
```

---

## 8. IPC server inside GNOME Shell (Unix socket)

### 8.1 Server strategy
Use:
- `Gio.SocketService`
- accept connections
- read lines with `Gio.DataInputStream`
- write with `Gio.DataOutputStream`

### 8.2 Skeleton server
```js
class BrokerServer {
  constructor() {
    this._service = null;
    this._connections = new Set();
  }

  start() {
    if (this._service) return;

    // Remove old socket if present
    try { GLib.unlink(sockPath()); } catch (e) {}

    this._service = new Gio.SocketService();

    const addr = new Gio.UnixSocketAddress({ path: sockPath() });
    this._service.add_address(
      addr,
      Gio.SocketType.STREAM,
      Gio.SocketProtocol.DEFAULT,
      null
    );

    // Best-effort permissions
    try { GLib.chmod(sockPath(), 0o600); } catch (e) {}

    this._service.connect('incoming', (service, connection) => {
      this._handleConnection(connection);
      return true;
    });

    this._service.start();
    log(`AutomationBroker: started socket at ${sockPath()}`);
  }

  stop() {
    if (!this._service) return;

    for (const c of this._connections) {
      try { c.close(null); } catch (e) {}
    }
    this._connections.clear();

    try { this._service.stop(); } catch (e) {}
    this._service = null;

    try { GLib.unlink(sockPath()); } catch (e) {}
    log(`AutomationBroker: stopped`);
  }

  _handleConnection(connection) {
    this._connections.add(connection);

    const istream = connection.get_input_stream();
    const ostream = connection.get_output_stream();

    const din = new Gio.DataInputStream({ base_stream: istream });
    const dout = new Gio.DataOutputStream({ base_stream: ostream });

    const readLoop = () => {
      din.read_line_async(GLib.PRIORITY_DEFAULT, null, (obj, res) => {
        try {
          const [line, length] = din.read_line_finish(res);
          if (!line) { this._connections.delete(connection); return; }

          const text = (new TextDecoder()).decode(line);
          const reply = this._dispatch(text);
          dout.put_string(reply + "\n", null);

          readLoop();
        } catch (e) {
          try { connection.close(null); } catch (e2) {}
          this._connections.delete(connection);
        }
      });
    };

    readLoop();
  }

  _dispatch(lineText) {
    let msg = null;
    try {
      msg = JSON.parse(lineText);
    } catch {
      return JSON.stringify({ id: null, ok: false, error: { code: "BAD_JSON", message: "Invalid JSON" }});
    }

    const id = msg.id ?? null;
    const method = msg.method ?? "";
    const params = msg.params ?? {};

    if (method !== "GetVersion") {
      const token = readToken();
      if (!token || params.token !== token) {
        return JSON.stringify({ id, ok: false, error: { code: "UNAUTHORIZED", message: "Invalid token" }});
      }
    }

    try {
      const result = this._handleMethod(method, params);
      return JSON.stringify({ id, ok: true, result });
    } catch (e) {
      return JSON.stringify({ id, ok: false, error: { code: "EXCEPTION", message: String(e) }});
    }
  }

  _handleMethod(method, params) {
    switch (method) {
      case "GetVersion":
        return { api_version: API_VERSION, gnome_version: "unknown" };
      case "ListOutputs":
        return listOutputs();
      case "ListWindows":
        return listWindows();
      default:
        throw new Error(`Unknown method: ${method}`);
    }
  }
}
```

---

## 9. Token monitoring (“armed” behavior)

```js
class TokenMonitor {
  constructor(onArmedChanged) {
    this._monitor = null;
    this._onArmedChanged = onArmedChanged;
  }

  start() {
    const file = Gio.File.new_for_path(tokenPath());
    this._monitor = file.monitor_file(Gio.FileMonitorFlags.NONE, null);
    this._monitor.connect('changed', () => this._onArmedChanged());
  }

  stop() {
    try { this._monitor?.cancel(); } catch {}
    this._monitor = null;
  }
}
```

---

## 10. Extension lifecycle: `enable()` / `disable()`

```js
let server = null;
let tokenMon = null;

export function enable() {
  server = new BrokerServer();
  tokenMon = new TokenMonitor(() => {
    const armed = (readToken() !== null);
    if (armed) server.start();
    else server.stop();
  });

  tokenMon.start();

  if (readToken() !== null) server.start();
}

export function disable() {
  try { tokenMon?.stop(); } catch {}
  tokenMon = null;

  try { server?.stop(); } catch {}
  server = null;
}
```

---

## 11. systemd user service unit

`~/.config/systemd/user/automation-broker.service`

```ini
[Unit]
Description=Automation Broker (GNOME Shell extension gate)
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=oneshot
RemainAfterExit=yes

ExecStart=/bin/bash -lc '  umask 077;   token_path="${XDG_RUNTIME_DIR}/automation-broker.token";   head -c 32 /dev/urandom | base64 > "${token_path}";   gnome-extensions enable com.yourorg.automationbroker@yourorg '

ExecStop=/bin/bash -lc '  gnome-extensions disable com.yourorg.automationbroker@yourorg || true;   rm -f "${XDG_RUNTIME_DIR}/automation-broker.token" "${XDG_RUNTIME_DIR}/automation-broker.sock" '

[Install]
WantedBy=default.target
```

---

## 12. CLI wrapper script

`~/.local/bin/automation-broker`

```bash
#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-}"
case "$cmd" in
  start)  systemctl --user start automation-broker.service ;;
  stop)   systemctl --user stop automation-broker.service ;;
  status)
    systemctl --user status automation-broker.service --no-pager
    echo "Socket: ${XDG_RUNTIME_DIR}/automation-broker.sock"
    ;;
  token-path) echo "${XDG_RUNTIME_DIR}/automation-broker.token" ;;
  *)
    echo "Usage: automation-broker {start|stop|status|token-path}"
    exit 1
    ;;
esac
```

---

## 13. Python client skeleton

```python
import json, os, socket

SOCK = os.path.join(os.environ["XDG_RUNTIME_DIR"], "automation-broker.sock")
TOKEN_PATH = os.path.join(os.environ["XDG_RUNTIME_DIR"], "automation-broker.token")

def read_token():
    with open(TOKEN_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

class BrokerClient:
    def __init__(self):
        self.token = read_token()
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(SOCK)
        self.f = self.sock.makefile("rwb", buffering=0)

    def call(self, method, params=None, msg_id=1):
        params = params or {}
        params.setdefault("token", self.token)
        req = {"id": msg_id, "method": method, "params": params}
        self.f.write((json.dumps(req) + "\n").encode("utf-8"))
        resp = json.loads(self.f.readline().decode("utf-8"))
        if not resp.get("ok"):
            raise RuntimeError(resp.get("error"))
        return resp["result"]

    def list_outputs(self): return self.call("ListOutputs")
    def list_windows(self): return self.call("ListWindows")

    def close(self):
        try: self.f.close()
        finally: self.sock.close()
```

---

## 14. Next-step checklist

1. Create extension folder + `metadata.json` + minimal `extension.js`.
2. Add token monitor + socket start/stop.
3. Add `ListOutputs` + `ListWindows`.
4. Add systemd user service + CLI.
5. Validate start/stop removes capability reliably.
6. Expand to mapping and subscriptions.

