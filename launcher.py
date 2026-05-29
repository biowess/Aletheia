"""
launcher.py — Clinical Workstation bootstrapper.
Orchestrates environment validation, dependency installation,
backend + frontend startup, and browser auto-launch.

Dependencies: standard library + rich
"""

import sys
import os
import subprocess
import platform

def bootstrap():
    # ── Prerequisite check ──────────────────────────────────────────────────
    ok = sys.version_info >= (3, 11)
    if not ok:
        print(f"Error: Python version {platform.python_version()} found, but launcher.py requires 3.11+.")
        sys.exit(1)

    backend_dir = os.path.abspath("backend")
    venv_dir = os.path.join(backend_dir, ".venv")
    is_windows = sys.platform == "win32"
    
    if is_windows:
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        
    # Check if we are running in the venv
    if os.path.normpath(sys.executable) == os.path.normpath(venv_python):
        return # We are already in the venv, proceed with the rest of the script.

    if not os.path.exists(venv_dir):
        print("creating virtual environment")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    else:
        print("using existing virtual environment")

    req_path = os.path.join(backend_dir, "requirements.txt")
    
    # Check if dependencies are already installed by trying to import rich and uvicorn
    res = subprocess.run([venv_python, "-c", "import rich, uvicorn"], capture_output=True)
    if res.returncode != 0:
        print("installing Python dependencies")
        subprocess.run(
            [venv_python, "-m", "pip", "install", "rich", "-r", req_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        print("dependencies already satisfied")
    
    # Re-execute this script inside the venv
    os.execl(venv_python, venv_python, *sys.argv)

# Run bootstrap before any third-party imports
bootstrap()

import time
import webbrowser
import threading
import socket
import argparse

# ── Rich traceback (catches all unhandled exceptions) ──────────────────────────
from rich.traceback import install as install_traceback
install_traceback(show_locals=True)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.status import Status
from rich.rule import Rule
from rich.theme import Theme

# ── Shared console ─────────────────────────────────────────────────────────────
theme = Theme(
    {
        "launcher": "bold green",
        "backend": "bold cyan",
        "frontend": "bold magenta",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "info": "dim white",
        "url": "underline bright_blue",
        "muted": "dim",
    }
)
console = Console(theme=theme, highlight=False)


# ── Helpers ────────────────────────────────────────────────────────────────────

def log(msg: str, style: str = "launcher") -> None:
    prefix = Text(f"[LAUNCHER] ", style=style)
    body = Text(msg)
    console.print(prefix + body)


def log_backend(msg: str) -> None:
    prefix = Text("[BACKEND]  ", style="backend")
    body = Text(msg.rstrip(), style="dim")
    console.print(prefix + body)


def log_frontend(msg: str) -> None:
    prefix = Text("[FRONTEND] ", style="frontend")
    body = Text(msg.rstrip(), style="dim")
    console.print(prefix + body)


def check_mark(ok: bool) -> Text:
    return Text("✔", style="success") if ok else Text("✘", style="error")


def stream_pipe(pipe, printer) -> None:
    """Read lines from *pipe* and forward to *printer* on a background thread."""
    try:
        for raw in iter(pipe.readline, b""):
            line = raw.decode(errors="replace").rstrip()
            if line:
                printer(line)
    finally:
        pipe.close()


def is_port_in_use(port: int) -> bool:
    """Check if a local TCP port is already in use using socket.socket."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def check_and_free_port(port: int, service_name: str) -> None:
    """Before launching, check if port is occupied. Warn, try to kill, or exit."""
    if not is_port_in_use(port):
        return

    console.print(
        Text("⚠", style="warning"),
        Text(f" Port {port} is already in use (blocking {service_name} startup)!", style="warning")
    )
    
    # Attempt to free the port on non-Windows platforms using standard Unix utilities
    if sys.platform != "win32":
        try:
            log(f"Attempting to free port {port} using fuser...", style="warning")
            # fuser -k {port}/tcp terminates processes using the port
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, check=False)
            time.sleep(1.0)
            
            # Fallback to lsof & kill if fuser was missing or failed
            if is_port_in_use(port):
                log(f"Port {port} still in use. Attempting kill using lsof...", style="warning")
                res = subprocess.run(["lsof", "-t", "-i", f"tcp:{port}"], capture_output=True, text=True, check=False)
                pids = res.stdout.strip().split()
                for pid in pids:
                    if pid:
                        subprocess.run(["kill", "-9", pid], check=False)
                time.sleep(1.0)
        except Exception as e:
            log(f"Failed to automatically free port: {e}", style="error")
            
    # Check again
    if is_port_in_use(port):
        console.print(
            Text("✘", style="error"),
            Text(f" Critical error: Port {port} is occupied and could not be freed automatically.", style="error")
        )
        log("Please stop any running instances or free the port manually and retry.", style="error")
        sys.exit(1)
    else:
        console.print(
            Text("✔", style="success"),
            Text(f" Port {port} has been successfully freed and is ready for use.", style="success")
        )


# ── Banner ─────────────────────────────────────────────────────────────────────

def print_banner() -> None:
    python_ver = platform.python_version()
    plat = platform.system()
    cwd = os.getcwd()

    content = Table.grid(padding=(0, 2))
    content.add_column(justify="left", style="muted")
    content.add_column(justify="left")
    content.add_row("Python", f"[success]{python_ver}[/]")
    content.add_row("Platform", f"[info]{plat}[/]")
    content.add_row("Directory", f"[info]{cwd}[/]")

    panel = Panel(
        Align.center(content),
        title="[bold bright_white]⚕  Aletheia: Clinical Workstation[/]",
        subtitle="[muted]Developer Launcher[/]",
        border_style="bright_blue",
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Validation steps ───────────────────────────────────────────────────────────

def validate_python() -> None:
    ok = sys.version_info >= (3, 11)
    mark = check_mark(ok)
    ver = platform.python_version()
    label = Text(" Python version ", style="bold")
    if ok:
        console.print(mark, label, Text(f"{ver}", style="success"))
    else:
        console.print(mark, label, Text(f"{ver} — requires 3.11+", style="error"))
        sys.exit(1)


def validate_node() -> str:
    try:
        res = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, check=True, timeout=10
        )
        node_ver = res.stdout.strip()
        console.print(check_mark(True), Text(" Node.js version  ", style="bold"), Text(node_ver, style="success"))
        return node_ver
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        console.print(check_mark(False), Text(" Node.js          ", style="bold"), Text("not found in PATH", style="error"))
        sys.exit(1)


# ── Environment setup ──────────────────────────────────────────────────────────

def ensure_node_modules(npm_cmd: str, frontend_dir: str) -> None:
    node_modules = os.path.join(frontend_dir, "node_modules")
    if os.path.exists(node_modules):
        console.print(check_mark(True), Text(" Node modules     ", style="bold"), Text("already installed", style="muted"))
        return
    with Status("[bold cyan]Running npm install…[/]", console=console, spinner="dots2"):
        subprocess.run(
            [npm_cmd, "install"],
            cwd=frontend_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    console.print(check_mark(True), Text(" Node modules     ", style="bold"), Text("installed", style="success"))


# ── Summary table ──────────────────────────────────────────────────────────────

def print_summary(backend_dir: str, frontend_dir: str, venv_python: str, node_ver: str) -> None:
    console.print()
    console.print(Rule("[bold bright_white]Launch Configuration[/]", style="bright_blue"))
    console.print()

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        show_edge=False,
    )
    table.add_column(style="bold dim", justify="right", min_width=18)
    table.add_column(style="white")

    table.add_row("Backend dir",    f"[info]{backend_dir}[/]")
    table.add_row("Frontend dir",   f"[info]{frontend_dir}[/]")
    table.add_row("Backend URL",    "[url]http://localhost:8000[/]")
    table.add_row("Frontend URL",   "[url]http://localhost:5173[/]")
    table.add_row("Python exec",    f"[info]{venv_python}[/]")
    table.add_row("Node.js",        f"[info]{node_ver}[/]")

    console.print(Align.center(table))
    console.print()


# ── Process startup ────────────────────────────────────────────────────────────

def start_backend(venv_python: str, backend_dir: str) -> subprocess.Popen:
    check_and_free_port(8000, "Backend")
    with Status("[bold cyan]Starting backend server…[/]", console=console, spinner="bouncingBall"):
        proc = subprocess.Popen(
            [venv_python, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(0.5)  # small grace period for immediate crash detection
        if proc.poll() is not None:
            console.print(check_mark(False), Text(" Backend          ", style="bold"), Text(f"crashed on startup (exit {proc.returncode})", style="error"))
            sys.exit(1)

    console.print(check_mark(True), Text(" Backend          ", style="bold"), Text(f"running  [muted](PID {proc.pid})[/]", style="backend"))
    threading.Thread(target=stream_pipe, args=(proc.stdout, log_backend), daemon=True).start()
    return proc


def start_frontend(npm_cmd: str, frontend_dir: str) -> subprocess.Popen:
    check_and_free_port(5173, "Frontend")
    with Status("[bold cyan]Starting frontend server…[/]", console=console, spinner="bouncingBall"):
        proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(0.5)
        if proc.poll() is not None:
            console.print(check_mark(False), Text(" Frontend         ", style="bold"), Text(f"crashed on startup (exit {proc.returncode})", style="error"))
            sys.exit(1)

    console.print(check_mark(True), Text(" Frontend         ", style="bold"), Text(f"running  [muted](PID {proc.pid})[/]", style="frontend"))
    threading.Thread(target=stream_pipe, args=(proc.stdout, log_frontend), daemon=True).start()
    return proc


# ── Ready panel ────────────────────────────────────────────────────────────────

def print_ready_panel() -> None:
    content = Table.grid(padding=(0, 2))
    content.add_column(justify="right", style="dim")
    content.add_column(justify="left")
    content.add_row("API   →", "[url]http://localhost:8000[/]")
    content.add_row("Docs  →", "[url]http://localhost:8000/docs[/]")
    content.add_row("App   →", "[url]http://localhost:5173[/]")

    panel = Panel(
        Align.center(content),
        title="[bold bright_green]✔  Workstation Ready[/]",
        subtitle="[muted]Press Ctrl+C to stop[/]",
        border_style="bright_green",
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Shutdown ───────────────────────────────────────────────────────────────────

def graceful_shutdown(backend_process, frontend_process) -> None:
    console.print()
    with Status("[bold yellow]Stopping workstation…[/]", console=console, spinner="dots"):
        processes = []
        if backend_process and backend_process.poll() is None:
            log("Sending SIGTERM to Backend...", style="warning")
            backend_process.terminate()
            processes.append((backend_process, "backend"))
        if frontend_process and frontend_process.poll() is None:
            log("Sending SIGTERM to Frontend...", style="warning")
            frontend_process.terminate()
            processes.append((frontend_process, "frontend"))
            
        start_time = time.time()
        while processes and (time.time() - start_time) < 5.0:
            still_running = []
            for proc, name in processes:
                if proc.poll() is None:
                    still_running.append((proc, name))
                else:
                    log(f"{name.capitalize()} exited gracefully.", style="success")
            processes = still_running
            if processes:
                time.sleep(0.1)
                
        # Force kill any that didn't terminate in 5 seconds
        for proc, name in processes:
            if proc.poll() is None:
                log(f"{name.capitalize()} did not exit in 5 seconds. Force-killing...", style="error")
                proc.kill()
                proc.wait()

    panel = Panel(
        Align.center(Text("Workstation stopped.", style="bold yellow")),
        border_style="yellow",
        padding=(1, 4),
    )
    console.print()
    console.print(panel)
    console.print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── Parse CLI arguments ──────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Clinical Workstation Bootstrapper")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip opening the web browser automatically on startup"
    )
    args = parser.parse_args()

    # ── Banner ──────────────────────────────────────────────────────────────────
    print_banner()

    console.print(Rule("[bold bright_white]Environment Validation[/]", style="bright_blue"))
    console.print()

    # ── Prerequisite checks ─────────────────────────────────────────────────────
    validate_python()
    node_ver = validate_node()

    # ── Path resolution ─────────────────────────────────────────────────────────
    is_windows  = sys.platform == "win32"
    backend_dir = os.path.abspath("backend")
    frontend_dir = os.path.abspath("frontend")
    venv_dir    = os.path.join(backend_dir, ".venv")

    if is_windows:
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        npm_cmd = "npm.cmd"
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        npm_cmd = "npm"

    ensure_node_modules(npm_cmd, frontend_dir)

    # ── Summary ─────────────────────────────────────────────────────────────────
    print_summary(backend_dir, frontend_dir, venv_python, node_ver)

    # ── Process startup ─────────────────────────────────────────────────────────
    console.print(Rule("[bold bright_white]Starting Services[/]", style="bright_blue"))
    console.print()

    backend_process  = None
    frontend_process = None

    try:
        backend_process  = start_backend(venv_python, backend_dir)
        frontend_process = start_frontend(npm_cmd, frontend_dir)

        # ── Browser launch ───────────────────────────────────────────────────────
        console.print()
        log("Waiting 3 s for servers to initialise…", style="launcher")
        time.sleep(3)
        if not args.no_browser:
            log("Opening browser → [url]http://localhost:5173[/]", style="launcher")
            webbrowser.open("http://localhost:5173")
        else:
            log("Skipping browser auto-launch due to --no-browser flag.", style="launcher")

        print_ready_panel()

        # ── Stream logs until both processes exit ────────────────────────────────
        console.print(Rule("[bold bright_white]Process Logs[/]", style="bright_blue"))
        console.print()

        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        graceful_shutdown(backend_process, frontend_process)
        sys.exit(0)


if __name__ == "__main__":
    main()
