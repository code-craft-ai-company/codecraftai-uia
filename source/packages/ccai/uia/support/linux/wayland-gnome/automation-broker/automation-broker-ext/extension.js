
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const API_VERSION = "1.0";
const TOKEN_FILE = "automation-broker.token";
const SOCK_FILE = "automation-broker.sock";

// --- Helper: runtime paths ---

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

// --- Helper: token read ---

function readToken() {
    const path = tokenPath();
    const file = Gio.File.new_for_path(path);
    if (!file.query_exists(null)) return null;

    try {
        const [ok, contents] = file.load_contents(null);
        if (!ok) return null;
        return (new TextDecoder()).decode(contents).trim();
    } catch (e) {
        return null;
    }
}

// --- Output enumeration (monitors) ---

function listOutputs() {
    // Main.layoutManager.monitors is often easiest for logical geometry.
    // Each monitor object typically includes x, y, width, height.
    const monitors = Main.layoutManager.monitors || [];
    const primaryIndex = Main.layoutManager.primaryIndex ?? 0;

    return monitors.map((m, idx) => {
        // scale: can be global or per-monitor depending on fractional scaling
        // Some environments expose monitor.scale or global.display.get_monitor_scale(idx)
        const scale = (m.scale !== undefined) ? m.scale : 1.0;

        const logical = { x: m.x, y: m.y, w: m.width, h: m.height };

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

// --- Window enumeration ---

function windowToObject(metaWindow, outputs) {
    const title = metaWindow.get_title?.() ?? "";
    const appId = metaWindow.get_gtk_application_id?.()
        ?? metaWindow.get_wm_class?.()
        ?? metaWindow.get_wm_class_instance?.()
        ?? null;

    const rect = metaWindow.get_frame_rect?.() ?? metaWindow.get_outer_rect?.();
    const rectLogical = { x: rect.x, y: rect.y, w: rect.width, h: rect.height };

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

// --- IPC server inside GNOME Shell (Unix socket) ---

class BrokerServer {
    constructor() {
        this._service = null;
        this._connections = new Set();
    }

    start() {
        if (this._service) return;

        // Remove old socket if present
        try { GLib.unlink(sockPath()); } catch (e) { }

        this._service = new Gio.SocketService();

        const addr = new Gio.UnixSocketAddress({ path: sockPath() });
        this._service.add_address(
            addr,
            Gio.SocketType.STREAM,
            Gio.SocketProtocol.default,
            null
        );

        // Best-effort permissions
        try { GLib.chmod(sockPath(), 0o600); } catch (e) { }

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
            try { c.close(null); } catch (e) { }
        }
        this._connections.clear();

        try { this._service.stop(); } catch (e) { }
        this._service = null;

        try { GLib.unlink(sockPath()); } catch (e) { }
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
                    try { connection.close(null); } catch (e2) { }
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
            return JSON.stringify({ id: null, ok: false, error: { code: "BAD_JSON", message: "Invalid JSON" } });
        }

        const id = msg.id ?? null;
        const method = msg.method ?? "";
        const params = msg.params ?? {};

        if (method !== "GetVersion") {
            const token = readToken();
            if (!token || params.token !== token) {
                return JSON.stringify({ id, ok: false, error: { code: "UNAUTHORIZED", message: "Invalid token" } });
            }
        }

        try {
            const result = this._handleMethod(method, params);
            return JSON.stringify({ id, ok: true, result });
        } catch (e) {
            return JSON.stringify({ id, ok: false, error: { code: "EXCEPTION", message: String(e) } });
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

// --- Token monitoring (“armed” behavior) ---

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
        try { this._monitor?.cancel(); } catch { }
        this._monitor = null;
    }
}

// --- Extension lifecycle ---

let server = null;
let tokenMon = null;

export default class AutomationBrokerExtension {
    enable() {
        server = new BrokerServer();
        tokenMon = new TokenMonitor(() => {
            const armed = (readToken() !== null);
            if (armed) server.start();
            else server.stop();
        });

        tokenMon.start();

        if (readToken() !== null) server.start();
    }

    disable() {
        try { tokenMon?.stop(); } catch { }
        tokenMon = null;

        try { server?.stop(); } catch { }
        server = null;
    }
}
