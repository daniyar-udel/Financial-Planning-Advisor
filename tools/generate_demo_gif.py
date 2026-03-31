from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
WEB_DIST = ROOT / "web" / "dist"
OUTPUT_PATH = ROOT / "docs" / "financial-assistant-demo.gif"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"
WINDOW_SIZE = (1440, 960)
GIF_SIZE = (1100, 733)
TRANSITION_FRAMES = 6
TRANSITION_DURATION_MS = 90
SCREEN_HOLD_MS = 950
FINAL_HOLD_MS = 1400
ROUTES = [
    ("/invest", "invest"),
    ("/onboarding", "onboarding"),
    ("/strategy/result", "result"),
    ("/app/overview", "overview"),
    ("/app/simulation", "simulation"),
]


class DemoStaticHandler(SimpleHTTPRequestHandler):
    dist_dir = WEB_DIST
    state: dict[str, Any] = {}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(self.dist_dir), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlsplit(self.path)

        if parsed.path == "/__demo_bootstrap__.html":
            self._serve_bootstrap(parsed)
            return

        if self._serve_static_file(parsed.path):
            return

        self.path = "/index.html"
        super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _serve_bootstrap(self, parsed: urllib.parse.SplitResult) -> None:
        route = urllib.parse.parse_qs(parsed.query).get("route", ["/invest"])[0]
        payload = json.dumps(
            {
                "route": route,
                "token": self.state["token"],
                "result": self.state["result"],
            }
        ).replace("</", "<\\/")

        html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Demo bootstrap</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      body {{
        margin: 0;
        display: grid;
        place-items: center;
        min-height: 100vh;
        background: #f3efe6;
        color: #1f2937;
        font: 600 16px/1.4 Arial, sans-serif;
      }}
    </style>
  </head>
  <body>
    Preparing demo screen...
    <script>
      const demo = {payload};
      localStorage.setItem("aisa_auth_token", demo.token);
      sessionStorage.setItem("strategy_result", JSON.stringify(demo.result));
      window.location.replace(demo.route);
    </script>
  </body>
</html>
"""

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static_file(self, request_path: str) -> bool:
        path = request_path or "/"
        candidate = (self.dist_dir / path.lstrip("/")).resolve()

        if candidate.is_file() and candidate.is_relative_to(self.dist_dir):
            self.path = path
            super().do_GET()
            return True

        if Path(path).suffix:
            self.send_error(404, "File not found")
            return True

        return False


def ensure_frontend_bundle() -> None:
    if (WEB_DIST / "index.html").exists():
        return

    npm = "npm.cmd" if os.name == "nt" else "npm"
    print("Building frontend bundle...")
    subprocess.run([npm, "run", "build"], cwd=ROOT / "web", check=True)


def find_browser() -> Path:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("Chrome/Edge was not found in a standard installation path.")


def wait_for_url(url: str, timeout: float = 45.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(0.5)

    raise TimeoutError(f"Timed out waiting for {url}. Last error: {last_error}")


def start_backend() -> subprocess.Popen[Any]:
    python_executable = ROOT / ".venv" / "Scripts" / "python.exe"
    if not python_executable.exists():
        python_executable = Path(sys.executable)

    demo_data_dir = ROOT / ".demo"
    demo_data_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env.update(
        {
            "JWT_SECRET": "demo-jwt-secret-for-gif-generation",
            "DATABASE_PATH": str((demo_data_dir / "app.db").resolve()),
            "ALLOWED_ORIGINS": FRONTEND_URL,
        }
    )

    stdout = subprocess.DEVNULL
    stderr = subprocess.DEVNULL
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        [
            str(python_executable),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=ROOT,
        env=env,
        stdout=stdout,
        stderr=stderr,
        creationflags=creationflags,
    )

    wait_for_url(f"{BACKEND_URL}/health")
    return process


def stop_process(process: subprocess.Popen[Any] | None) -> None:
    if process is None or process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def request_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request_headers = {"Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with {exc.code}: {error_body}") from exc

    return json.loads(raw)


def build_demo_state() -> dict[str, Any]:
    timestamp = int(time.time())
    signup_payload = {
        "full_name": "Demo Investor",
        "email": f"demo-investor-{timestamp}@example.com",
        "password": "DemoPass123!",
    }
    signup_response = request_json("POST", f"{BACKEND_URL}/auth/signup", signup_payload)
    token = signup_response["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}

    onboarding_payload = {
        "goal_type": "long_term_wealth",
        "goal_amount": 500000,
        "investment_horizon_years": 25,
        "age": 28,
        "date_of_birth": "1998-01-01",
        "marital_status": "single",
        "address": "245 Market Street, New York, NY",
        "annual_income": 90000,
        "current_savings": 15000,
        "monthly_contribution": 800,
        "savings_rate": 0.15,
        "risk_preference": "medium",
        "stress_response": "hold",
        "strategy_preference": "classic",
    }
    request_json(
        "POST",
        f"{BACKEND_URL}/onboarding/profile",
        onboarding_payload,
        headers=auth_headers,
    )
    strategy_result = request_json(
        "GET",
        f"{BACKEND_URL}/strategy/result",
        headers=auth_headers,
    )

    return {"token": token, "result": strategy_result}


def start_frontend_server(state: dict[str, Any]) -> tuple[ThreadingHTTPServer, threading.Thread]:
    handler_class = type("BoundDemoStaticHandler", (DemoStaticHandler,), {})
    handler_class.state = state

    server = ThreadingHTTPServer(("127.0.0.1", 5173), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    wait_for_url(FRONTEND_URL)
    return server, thread


def capture_screenshot(browser_path: Path, route: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quoted_route = urllib.parse.quote(route, safe="")
    url = f"{FRONTEND_URL}/__demo_bootstrap__.html?route={quoted_route}"

    shared_args = [
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--run-all-compositor-stages-before-draw",
        f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}",
        "--virtual-time-budget=7000",
        f"--screenshot={output_path}",
        url,
    ]
    attempts = [
        [str(browser_path), "--headless=new", *shared_args],
        [str(browser_path), "--headless", *shared_args],
    ]

    last_error: Exception | None = None
    for command in attempts:
        try:
            subprocess.run(
                command,
                check=True,
                timeout=30,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if output_path.exists():
                return
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise RuntimeError(f"Could not capture {route}. Last error: {last_error}")


def prepare_frame(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    return image.resize(GIF_SIZE, Image.Resampling.LANCZOS)


def build_gif(screenshot_paths: list[Path], output_path: Path) -> None:
    prepared = [prepare_frame(path) for path in screenshot_paths]
    frames: list[Image.Image] = []
    durations: list[int] = []

    for index, current in enumerate(prepared):
        frames.append(current)
        durations.append(FINAL_HOLD_MS if index == len(prepared) - 1 else SCREEN_HOLD_MS)

        if index == len(prepared) - 1:
            continue

        next_frame = prepared[index + 1]
        for step in range(1, TRANSITION_FRAMES + 1):
            alpha = step / (TRANSITION_FRAMES + 1)
            frames.append(Image.blend(current, next_frame, alpha))
            durations.append(TRANSITION_DURATION_MS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    ensure_frontend_bundle()
    browser_path = find_browser()
    backend_process: subprocess.Popen[Any] | None = None
    frontend_server: ThreadingHTTPServer | None = None

    try:
        print("Starting backend...")
        backend_process = start_backend()

        print("Preparing demo data...")
        state = build_demo_state()

        print("Starting frontend server...")
        frontend_server, _ = start_frontend_server(state)

        screenshot_dir = ROOT / ".demo" / "screens"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_paths: list[Path] = []
        for route, name in ROUTES:
            path = screenshot_dir / f"{name}.png"
            print(f"Capturing {route}...")
            capture_screenshot(browser_path, route, path)
            screenshot_paths.append(path)

        print(f"Building GIF at {OUTPUT_PATH}...")
        build_gif(screenshot_paths, OUTPUT_PATH)
        print(f"GIF created: {OUTPUT_PATH}")
    finally:
        if frontend_server is not None:
            frontend_server.shutdown()
            frontend_server.server_close()
        stop_process(backend_process)


if __name__ == "__main__":
    main()
