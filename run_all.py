#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
import webbrowser


ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
REQ_FILE = BACKEND_DIR / "requirements.txt"
VENV_DIR = ROOT / ".venv"
CONFIG_FILE = ROOT / "config.json"


def load_config():
    """Load configuration from config.json."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load config.json: {e}")
        # Return minimal defaults if config file is missing
        return {
            "backend": {"host": "0.0.0.0", "port": 8000},
            "frontend": {"port": 5173, "auto_open_browser": True}
        }


def venv_python(venv: Path) -> Path:
    if platform.system().lower().startswith("win"):
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def ensure_venv(venv: Path) -> Path:
    py = venv_python(venv)
    if not py.exists():
        print(f"[setup] Creating venv at {venv}")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv)])
    return py


def pip_install(py: Path, requirements: Path):
    print(f"[setup] Installing requirements from {requirements}")
    subprocess.check_call([str(py), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])  # noqa: E501
    subprocess.check_call([str(py), "-m", "pip", "install", "-r", str(requirements)])


def spawn(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> subprocess.Popen:
    print(f"[run] {' '.join(cmd)} (cwd={cwd or ROOT})")
    return subprocess.Popen(cmd, cwd=str(cwd or ROOT), env=env, creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP') else 0))  # type: ignore[attr-defined]


def terminate(proc: subprocess.Popen):
    if proc.poll() is not None:
        return
    try:
        if platform.system().lower().startswith("win"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
            time.sleep(0.3)
            proc.terminate()
        else:
            proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
    except Exception:
        pass


def main():
    # Load configuration from config.json
    config = load_config()

    # Get defaults from config
    default_backend_host = config.get("backend", {}).get("host", "0.0.0.0")
    default_backend_port = config.get("backend", {}).get("port", 8000)
    default_frontend_port = config.get("frontend", {}).get("port", 5173)
    default_auto_open = config.get("frontend", {}).get("auto_open_browser", True)
    default_reload = config.get("backend", {}).get("reload", False)

    parser = argparse.ArgumentParser(
        description="Run backend (FastAPI) and frontend (static) together",
        epilog="Note: Default values are loaded from config.json and can be overridden with arguments or environment variables."
    )
    parser.add_argument("--backend-host", default=default_backend_host, help=f"Backend host (default from config: {default_backend_host})")
    parser.add_argument("--backend-port", type=int, default=default_backend_port, help=f"Backend port (default from config: {default_backend_port})")
    parser.add_argument("--frontend-port", type=int, default=default_frontend_port, help=f"Frontend port (default from config: {default_frontend_port})")
    parser.add_argument("--device", choices=["cpu", "cuda", "auto"], default=None, help="Force device for backend model")
    parser.add_argument("--model-path", default=None, help="Path to .pth/.pt model file")
    parser.add_argument("--max-upload-mb", type=int, default=None, help="Max upload size in MB")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    parser.add_argument("--reload", action="store_true", default=default_reload, help=f"Run backend with --reload (default from config: {default_reload})")
    args = parser.parse_args()

    # Determine if browser should be opened (config default, unless --no-browser is specified)
    should_open_browser = default_auto_open and not args.no_browser

    # Ensure dirs exist for backend data
    for d in [BACKEND_DIR / "data" / "uploads", BACKEND_DIR / "data" / "outputs", BACKEND_DIR / "data" / "models"]:
        d.mkdir(parents=True, exist_ok=True)

    py = ensure_venv(VENV_DIR)
    pip_install(py, REQ_FILE)

    env = os.environ.copy()
    if args.device:
        env["DEVICE"] = args.device
    if args.model_path:
        env["MODEL_PATH"] = args.model_path
    if args.max_upload_mb is not None:
        env["MAX_UPLOAD_MB"] = str(args.max_upload_mb)

    backend_cmd = [
        str(py), "-m", "uvicorn", "backend.app:app",
        "--host", args.backend_host,
        "--port", str(args.backend_port),
    ]
    if args.reload:
        backend_cmd.append("--reload")

    frontend_cmd = [str(py), "-m", "http.server", str(args.frontend_port)]

    backend_proc = spawn(backend_cmd, cwd=ROOT, env=env)
    frontend_proc = spawn(frontend_cmd, cwd=FRONTEND_DIR, env=env)

    def cleanup():
        print("\n[cleanup] Shutting down processes...")
        terminate(frontend_proc)
        terminate(backend_proc)
        print("[cleanup] Done.")

    atexit.register(cleanup)

    frontend_url = f"http://localhost:{args.frontend_port}"
    print("\nServices running:")
    print(f"- Backend: http://localhost:{args.backend_port}")
    print(f"- Frontend: {frontend_url}")
    print(f"\nConfiguration loaded from: {CONFIG_FILE}")

    if should_open_browser:
        print("Opening browser...")
        try:
            webbrowser.open(frontend_url)
        except Exception as e:
            print(f"Could not open browser: {e}")

    try:
        # Wait on children; if either exits, exit
        while True:
            time.sleep(0.5)
            c1 = backend_proc.poll()
            c2 = frontend_proc.poll()
            if c1 is not None or c2 is not None:
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()

