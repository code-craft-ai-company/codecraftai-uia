
import socket
import json
import os
import pathlib

class BrokerClient:
    """
    Client for the Gnome Shell Automation Broker.
    Connects to the Unix domain socket exposed by the extension.
    """
    TOKEN_FILE = "automation-broker.token"
    SOCK_FILE = "automation-broker.sock"

    def __init__(self):
        self._runtime_dir = pathlib.Path(os.environ.get("XDG_RUNTIME_DIR", "/run/user/1000"))
        self._sock_path = self._runtime_dir / self.SOCK_FILE
        self._token_path = self._runtime_dir / self.TOKEN_FILE
        self._token = self._read_token()
        self._next_req_id = 1
        return

    def _read_token(self):
        try:
            with open(self._token_path, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def _call_method(self, method, params=None):
        if not self._token:
             # Try refreshing token
             self._token = self._read_token()
             if not self._token:
                 raise RuntimeError("Automation Broker token not found. Is the service running?")

        if not self._sock_path.exists():
            raise RuntimeError(f"Automation Broker socket not found at {self._sock_path}")

        req_id = self._next_req_id
        self._next_req_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": req_id
        }
        # Inject token
        payload["params"]["token"] = self._token
        
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(str(self._sock_path))
            
            msg = json.dumps(payload) + "\n"
            client.sendall(msg.encode('utf-8'))
            
            # Read response (simple line-based for now as per server implementation)
            response_data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                if b"\n" in chunk: # rudimentary framing check
                     break
            
            client.close()
            
            resp = json.loads(response_data.decode('utf-8'))
            if "error" in resp and resp["error"] is not None:
                error = resp["error"]
                raise RuntimeError(f"Broker error: {error.get('code')} - {error.get('message')}")

            return resp.get("result")
            
        except Exception as e:
            raise RuntimeError(f"Broker communication failed: {e}")

    def list_windows(self):
        """Returns a list of open windows with coordinates."""
        return self._call_method("ListWindows")

    def list_outputs(self):
        """Returns a list of monitors/outputs."""
        return self._call_method("ListOutputs")
    
    def get_version(self):
        return self._call_method("GetVersion")
