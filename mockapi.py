"""Simple LOCAL HTTP server with two event pages and a deliberate error endpoint."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        page = parse_qs(parsed.query).get("page", ["1"])[0]

        if parsed.path == "/logs":
            if page == "1":
                data = {"events": [{"EventID": 4625, "Username": "alice", "SourceIP": "192.0.2.10"}], "has_next": True}
            elif page == "2":
                data = {"events": [{"EventID": 4625, "Username": "bob", "SourceIP": "198.51.100.20"}], "has_next": False}
            else:
                self.send_error(404)
                return
        elif parsed.path == "/error/logs":
            self.send_error(503)
            return
        else:
            self.send_error(404)
            return

        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Do not log request headers (which may contain credentials).


if __name__ == "__main__":
    print("Mock API: http://127.0.0.1:8000/logs", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8000), MockHandler).serve_forever()
